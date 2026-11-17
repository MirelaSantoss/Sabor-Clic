const containerPedidos = document.getElementById("meus-pedidos");
const formReservaBancada = document.getElementById("form-reserva-bancada");
const selectBancada = document.getElementById("select-bancada");
const containerReservas = document.getElementById("minhas-reservas");
const mensagemReserva = document.getElementById("mensagem-reserva");

async function carregarPedidosCliente() {
    if (!containerPedidos) {
        return;
    }
    containerPedidos.textContent = "Carregando seus pedidos...";
    try {
        const resposta = await fetch("/pedidos");
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao carregar pedidos.");
        }

        containerPedidos.replaceChildren();
        const pedidos = dados.map(item => new Pedido(item));

        if (pedidos.length === 0) {
            containerPedidos.textContent = "Você ainda não fez pedidos.";
            return;
        }

        pedidos.forEach(pedido => {
            const card = document.createElement("article");
            card.className = "item-carrinho";

            const bloco = document.createElement("div");
            bloco.style.flex = "1";

            const titulo = document.createElement("h3");
            titulo.textContent = `Pedido #${pedido.id}`;

            const descricaoItens = pedido.itens
                .map(i => {
                    const obs = i.observacoes ? ` [${i.observacoes}]` : "";
                    return `${i.quantidade}× ${i.nome}${obs}`;
                })
                .join(", ");

            const paragrafoItens = document.createElement("p");
            paragrafoItens.textContent = `Itens: ${descricaoItens}`;

            const paragrafoStatus = document.createElement("p");
            const textoTempo = pedido.tempoEstimado ? ` · Tempo estimado: ${pedido.tempoEstimado} min` : "";
            paragrafoStatus.textContent = `Status: ${pedido.status}${textoTempo}`;

            const paragrafoTotal = document.createElement("strong");
            paragrafoTotal.textContent = `Total: ${pedido.totalFormatado}`;

            bloco.append(titulo, paragrafoItens, paragrafoStatus);

            if (pedido.observacoes) {
                const paragrafoObs = document.createElement("p");
                paragrafoObs.textContent = `Observações: ${pedido.observacoes}`;
                bloco.append(paragrafoObs);
            }

            bloco.append(paragrafoTotal);
            card.append(bloco);
            containerPedidos.appendChild(card);
        });
    } catch (erro) {
        containerPedidos.textContent = erro.message;
    }
}

async function carregarBancadasEReservas() {
    if (!selectBancada && !containerReservas) {
        return;
    }

    try {
        const [respBancadas, respReservas] = await Promise.all([
            fetch("/api/bancadas"),
            fetch("/api/bancadas/reservas")
        ]);

        if (respBancadas.ok && selectBancada) {
            const lista = (await respBancadas.json()).map(b => new Bancada(b));
            selectBancada.replaceChildren();
            lista.forEach(b => {
                const opt = document.createElement("option");
                opt.value = b.id;
                opt.textContent = `${b.codigo} — ${b.valorHoraFormatado}/h (Caução: ${b.valorCaucaoFormatado}) · ${b.descricao}`;
                selectBancada.append(opt);
            });
        }

        if (respReservas.ok && containerReservas) {
            const reservas = await respReservas.json();
            containerReservas.replaceChildren();
            if (!reservas.length) {
                containerReservas.textContent = "Nenhuma reserva de bancada registrada.";
            } else {
                reservas.forEach(r => {
                    const card = document.createElement("article");
                    card.className = "produto-admin";
                    const texto = document.createElement("span");
                    texto.textContent = `${r.cod_identificacao} | ${r.data_hora_inicio} até ${r.data_hora_fim} | Locação: ${Prato.formatarMoeda(r.valor_total_horas)} | Caução: ${Prato.formatarMoeda(r.valor_caucao_pago)} (${r.status_reserva})`;
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

carregarPedidosCliente();
carregarBancadasEReservas();
