const catalogoBancadas = document.getElementById("catalogo-bancadas");
const formReservaBancada = document.getElementById("form-reserva-bancada");
const selectBancada = document.getElementById("select-bancada");
const containerReservas = document.getElementById("minhas-reservas");
const mensagemReserva = document.getElementById("mensagem-reserva");

async function carregarBancadasEReservas() {
    try {
        const [respBancadas, respReservas] = await Promise.all([
            fetch("/api/bancadas"),
            fetch("/api/bancadas/reservas")
        ]);

        if (!respBancadas.ok || !respReservas.ok) {
            throw new Error("Erro ao carregar dados das bancadas.");
        }

        const listaBancadas = (await respBancadas.json()).map(b => new Bancada(b));
        const reservas = await respReservas.json();

        if (catalogoBancadas) {
            catalogoBancadas.replaceChildren();
            listaBancadas.forEach(bancada => {
                const card = document.createElement("article");
                card.className = "produto";

                const titulo = document.createElement("h3");
                titulo.textContent = bancada.codigo;

                const descricao = document.createElement("p");
                descricao.textContent = bancada.descricao;

                const valores = document.createElement("strong");
                valores.textContent = `${bancada.valorHoraFormatado}/hora`;

                const caucao = document.createElement("small");
                caucao.textContent = `Caução de equipamentos: ${bancada.valorCaucaoFormatado}`;

                const botaoSelecionar = document.createElement("button");
                botaoSelecionar.type = "button";
                botaoSelecionar.className = "botao-secundario";
                botaoSelecionar.textContent = "Selecionar esta bancada";
                botaoSelecionar.onclick = () => {
                    if (selectBancada) {
                        selectBancada.value = String(bancada.id);
                        selectBancada.focus();
                    }
                };

                card.append(titulo, descricao, valores, caucao, botaoSelecionar);
                catalogoBancadas.append(card);
            });
        }

        if (selectBancada) {
            selectBancada.replaceChildren();
            listaBancadas.forEach(bancada => {
                const opt = document.createElement("option");
                opt.value = bancada.id;
                opt.textContent = `${bancada.codigo} — ${bancada.valorHoraFormatado}/h (Caução: ${bancada.valorCaucaoFormatado})`;
                selectBancada.append(opt);
            });
        }

        if (containerReservas) {
            containerReservas.replaceChildren();
            if (!reservas.length) {
                containerReservas.textContent = "Você ainda não possui reservas de bancada agendadas.";
            } else {
                reservas.forEach(reserva => {
                    const card = document.createElement("article");
                    card.className = "produto-admin";
                    const texto = document.createElement("span");
                    texto.textContent = `${reserva.cod_identificacao} | ${reserva.data_hora_inicio} até ${reserva.data_hora_fim} | Locação: ${Prato.formatarMoeda(reserva.valor_total_horas)} | Caução: ${Prato.formatarMoeda(reserva.valor_caucao_pago)} (${reserva.status_reserva})`;
                    card.append(texto);
                    containerReservas.append(card);
                });
            }
        }
    } catch (erro) {
        if (mensagemReserva) {
            mensagemReserva.textContent = erro.message;
        }
    }
}

if (formReservaBancada) {
    formReservaBancada.addEventListener("submit", async evento => {
        evento.preventDefault();
        const formData = new FormData(formReservaBancada);
        const payload = Object.fromEntries(formData.entries());
        try {
            const resposta = await fetch("/api/bancadas/reservas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Não foi possível reservar a bancada.");
            }
            if (mensagemReserva) {
                mensagemReserva.textContent = `${dados.mensagem} Total horas: ${Prato.formatarMoeda(dados.valor_total_horas)} | Caução: ${Prato.formatarMoeda(dados.valor_caucao_pago)}`;
            }
            formReservaBancada.reset();
            await carregarBancadasEReservas();
        } catch (erro) {
            if (mensagemReserva) {
                mensagemReserva.textContent = erro.message;
            }
        }
    });
}

carregarBancadasEReservas();
