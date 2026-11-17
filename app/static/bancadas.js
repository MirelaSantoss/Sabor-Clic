const catalogoBancadas = document.getElementById("catalogo-bancadas");
const formReservaBancada = document.getElementById("form-reserva-bancada");
const selectBancada = document.getElementById("select-bancada");
const inputReservaInicio = document.getElementById("reserva-inicio");
const inputReservaFim = document.getElementById("reserva-fim");
const previaReservaParceiro = document.getElementById("previa-reserva-parceiro");
const btnConfirmarReserva = document.getElementById("btn-confirmar-reserva");

const containerReservas = document.getElementById("minhas-reservas");
const mensagemReserva = document.getElementById("mensagem-reserva");

const agendaOcupacaoParceiro = document.getElementById("agenda-ocupacao-parceiro");
const filtroAgendaBancada = document.getElementById("filtro-agenda-parceiro-bancada");
const filtroAgendaData = document.getElementById("filtro-agenda-parceiro-data");

const modalReagendar = document.getElementById("modal-reagendar-parceiro");
const formReagendar = document.getElementById("form-reagendar-parceiro");
const btnFecharReagendar = document.getElementById("fechar-modal-reagendar");
const avisoConflitoReagendar = document.getElementById("aviso-conflito-reagendar");

let cacheBancadas = [];
let cacheAgendaOcupada = [];

function normalizarDataHora(valor) {
    if (!valor) {
        return "";
    }
    const limpo = String(valor).trim().replace("T", " ");
    return limpo.length === 16 ? `${limpo}:00` : limpo.slice(0, 19);
}

function paraInputDateTimeLocal(dataSql) {
    if (!dataSql) {
        return "";
    }
    return String(dataSql).replace(" ", "T").slice(0, 16);
}

function atualizarPreviaEColisao() {
    if (!previaReservaParceiro || !selectBancada) {
        return;
    }

    const idBancada = Number(selectBancada.value);
    const bancada = cacheBancadas.find(b => b.id === idBancada);
    const inicio = normalizarDataHora(inputReservaInicio ? inputReservaInicio.value : "");
    const fim = normalizarDataHora(inputReservaFim ? inputReservaFim.value : "");

    if (!bancada || !inicio || !fim) {
        previaReservaParceiro.className = "aviso";
        previaReservaParceiro.textContent = "Selecione a bancada e o período para verificar disponibilidade e valores.";
        if (btnConfirmarReserva) {
            btnConfirmarReserva.disabled = false;
        }
        return;
    }

    const dtIni = new Date(inicio.replace(" ", "T"));
    const dtFim = new Date(fim.replace(" ", "T"));
    const horas = (dtFim - dtIni) / 3600000;

    if (Number.isNaN(horas) || horas < 1) {
        previaReservaParceiro.className = "aviso erro icone-inline";
        Icones.preencher(
            previaReservaParceiro,
            "alert",
            "O período mínimo de locação é de 1 hora (fim posterior ao início)."
        );
        if (btnConfirmarReserva) {
            btnConfirmarReserva.disabled = true;
        }
        return;
    }

    const conflito = cacheAgendaOcupada.find(slot =>
        Number(slot.bancada_id) === idBancada &&
        ["SOLICITADA", "CONFIRMADA"].includes(slot.status_reserva) &&
        String(slot.data_hora_inicio) < fim &&
        String(slot.data_hora_fim) > inicio
    );

    if (conflito) {
        previaReservaParceiro.className = "aviso erro icone-inline";
        Icones.preencher(
            previaReservaParceiro,
            "alert",
            `Horário indisponível! ${bancada.codigo} já está reservada das ${conflito.data_hora_inicio} até ${conflito.data_hora_fim}.`
        );
        if (btnConfirmarReserva) {
            btnConfirmarReserva.disabled = true;
        }
        return;
    }

    const valorHoras = horas * bancada.valorHora;
    const totalComCaucao = valorHoras + bancada.valorCaucao;
    previaReservaParceiro.className = "aviso icone-inline";
    Icones.preencher(
        previaReservaParceiro,
        "check",
        `Horário livre! Duração: ${horas.toFixed(1)}h · Valor horas: ${Prato.formatarMoeda(valorHoras)} · Caução: ${bancada.valorCaucaoFormatado} · Total c/ caução: ${Prato.formatarMoeda(totalComCaucao)}`
    );
    if (btnConfirmarReserva) {
        btnConfirmarReserva.disabled = false;
    }
}

function renderizarAgendaOcupacao() {
    if (!agendaOcupacaoParceiro) {
        return;
    }

    const bancadaFiltro = filtroAgendaBancada ? filtroAgendaBancada.value : "";
    const dataFiltro = filtroAgendaData ? filtroAgendaData.value : "";

    const filtrados = cacheAgendaOcupada.filter(slot => {
        if (bancadaFiltro && String(slot.bancada_id) !== String(bancadaFiltro)) {
            return false;
        }
        if (dataFiltro) {
            const ini = String(slot.data_hora_inicio || "").slice(0, 10);
            const fim = String(slot.data_hora_fim || "").slice(0, 10);
            if (ini > dataFiltro || fim < dataFiltro) {
                return false;
            }
        }
        return true;
    });

    agendaOcupacaoParceiro.replaceChildren();

    if (filtrados.length === 0) {
        agendaOcupacaoParceiro.textContent = "Nenhum horário ocupado encontrado para este filtro (todas as janelas estão livres).";
        return;
    }

    filtrados.forEach(slot => {
        const card = document.createElement("article");
        card.className = "produto-admin";

        const info = document.createElement("div");
        info.className = "info-prato-admin";
        info.style.flex = "1";

        const titulo = document.createElement("strong");
        titulo.textContent = `${slot.cod_identificacao} — Ocupada de ${slot.data_hora_inicio} até ${slot.data_hora_fim} (${slot.duracao_horas}h)`;

        const desc = document.createElement("small");
        desc.textContent = `Equipamentos: ${slot.bancada_descricao}`;

        info.append(titulo, desc);

        const badge = document.createElement("span");
        badge.className = "badge-alerta";
        badge.textContent = "OCUPADA";

        card.append(info, badge);
        agendaOcupacaoParceiro.append(card);
    });
}

function abrirModalReagendar(reserva) {
    if (!modalReagendar) {
        return;
    }
    document.getElementById("reagendar-id").value = reserva.id_reserva;
    document.getElementById("reagendar-bancada").value = String(reserva.bancada_id);
    document.getElementById("reagendar-inicio").value = paraInputDateTimeLocal(reserva.data_hora_inicio);
    document.getElementById("reagendar-fim").value = paraInputDateTimeLocal(reserva.data_hora_fim);
    avisoConflitoReagendar.textContent = "";
    modalReagendar.showModal();
}

async function cancelarReservaCliente(idReserva) {
    try {
        const resposta = await fetch(`/api/bancadas/reservas/${idReserva}`, {
            method: "DELETE"
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Não foi possível cancelar a reserva.");
        }
        if (mensagemReserva) {
            mensagemReserva.textContent = dados.mensagem;
        }
        await carregarBancadasEReservas();
    } catch (erro) {
        if (mensagemReserva) {
            mensagemReserva.textContent = erro.message;
        }
    }
}

async function carregarBancadasEReservas() {
    try {
        const [respBancadas, respReservas, respAgenda] = await Promise.all([
            fetch("/api/bancadas"),
            fetch("/api/bancadas/reservas"),
            fetch("/api/bancadas/agenda")
        ]);

        if (!respBancadas.ok || !respReservas.ok || !respAgenda.ok) {
            throw new Error("Erro ao carregar dados das bancadas e agenda.");
        }

        cacheBancadas = (await respBancadas.json()).map(b => new Bancada(b));
        const reservas = await respReservas.json();
        cacheAgendaOcupada = await respAgenda.json();

        if (catalogoBancadas) {
            catalogoBancadas.replaceChildren();
            cacheBancadas.forEach(bancada => {
                const ocupacoesDaBancada = cacheAgendaOcupada.filter(s => Number(s.bancada_id) === bancada.id);

                const card = document.createElement("article");
                card.className = "produto";

                const titulo = document.createElement("h3");
                titulo.textContent = `${bancada.codigo} (${bancada.statusOperacional})`;

                const descricao = document.createElement("p");
                descricao.textContent = bancada.descricao;

                const valores = document.createElement("strong");
                valores.textContent = `${bancada.valorHoraFormatado}/hora`;

                const caucao = document.createElement("small");
                caucao.textContent = `Caução de garantia: ${bancada.valorCaucaoFormatado} · Períodos reservados: ${ocupacoesDaBancada.length}`;

                const botaoSelecionar = document.createElement("button");
                botaoSelecionar.type = "button";
                botaoSelecionar.className = "botao-secundario";
                botaoSelecionar.textContent = "Selecionar e ver agenda";
                botaoSelecionar.onclick = () => {
                    if (selectBancada) {
                        selectBancada.value = String(bancada.id);
                    }
                    if (filtroAgendaBancada) {
                        filtroAgendaBancada.value = String(bancada.id);
                        renderizarAgendaOcupacao();
                    }
                    atualizarPreviaEColisao();
                    if (inputReservaInicio) {
                        inputReservaInicio.focus();
                    }
                };

                card.append(titulo, descricao, valores, caucao, botaoSelecionar);
                catalogoBancadas.append(card);
            });
        }

        const popularSelectBancadas = elementoSelect => {
            if (!elementoSelect) {
                return;
            }
            const valorAnterior = elementoSelect.value;
            elementoSelect.replaceChildren();
            cacheBancadas.forEach(bancada => {
                const opt = document.createElement("option");
                opt.value = String(bancada.id);
                opt.textContent = `${bancada.codigo} — ${bancada.valorHoraFormatado}/h (Caução: ${bancada.valorCaucaoFormatado})`;
                elementoSelect.append(opt);
            });
            if (valorAnterior) {
                elementoSelect.value = valorAnterior;
            }
        };

        popularSelectBancadas(selectBancada);
        popularSelectBancadas(document.getElementById("reagendar-bancada"));

        if (filtroAgendaBancada) {
            const valorAtual = filtroAgendaBancada.value;
            filtroAgendaBancada.replaceChildren();
            const optTodas = document.createElement("option");
            optTodas.value = "";
            optTodas.textContent = "Todas as bancadas";
            filtroAgendaBancada.append(optTodas);
            cacheBancadas.forEach(bancada => {
                const opt = document.createElement("option");
                opt.value = String(bancada.id);
                opt.textContent = bancada.codigo;
                filtroAgendaBancada.append(opt);
            });
            filtroAgendaBancada.value = valorAtual;
        }

        renderizarAgendaOcupacao();
        atualizarPreviaEColisao();

        if (containerReservas) {
            containerReservas.replaceChildren();
            if (!reservas.length) {
                containerReservas.textContent = "Você ainda não possui reservas de bancada agendadas.";
            } else {
                reservas.forEach(reserva => {
                    const card = document.createElement("article");
                    card.className = "produto-admin";

                    const info = document.createElement("div");
                    info.className = "info-prato-admin";
                    info.style.flex = "1";

                    const titulo = document.createElement("strong");
                    titulo.textContent = `Reserva #${reserva.id_reserva} · ${reserva.cod_identificacao} (${reserva.data_hora_inicio} até ${reserva.data_hora_fim})`;

                    const detalhes = document.createElement("small");
                    detalhes.textContent = `Equipamentos: ${reserva.bancada_descricao} · Locação: ${Prato.formatarMoeda(reserva.valor_total_horas)} | Caução: ${Prato.formatarMoeda(reserva.valor_caucao_pago)} | Adicionais: ${Prato.formatarMoeda(reserva.valor_adicionais)}`;

                    info.append(titulo, detalhes);

                    const badge = document.createElement("span");
                    badge.className = reserva.status_reserva === "CANCELADA" ? "badge-alerta" : "badge-normal";
                    badge.textContent = reserva.status_reserva;

                    card.append(info, badge);

                    if (["SOLICITADA", "CONFIRMADA"].includes(reserva.status_reserva)) {
                        const btnReagendar = document.createElement("button");
                        btnReagendar.type = "button";
                        btnReagendar.className = "botao";
                        btnReagendar.textContent = "Reagendar";
                        btnReagendar.onclick = () => abrirModalReagendar(reserva);

                        const btnCancelar = document.createElement("button");
                        btnCancelar.type = "button";
                        btnCancelar.className = "botao-secundario";
                        btnCancelar.textContent = "Cancelar";
                        btnCancelar.onclick = () => cancelarReservaCliente(reserva.id_reserva);

                        card.append(btnReagendar, btnCancelar);
                    }

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

if (selectBancada) {
    selectBancada.addEventListener("change", atualizarPreviaEColisao);
}
if (inputReservaInicio) {
    inputReservaInicio.addEventListener("input", atualizarPreviaEColisao);
}
if (inputReservaFim) {
    inputReservaFim.addEventListener("input", atualizarPreviaEColisao);
}

if (filtroAgendaBancada) {
    filtroAgendaBancada.addEventListener("change", renderizarAgendaOcupacao);
}
if (filtroAgendaData) {
    filtroAgendaData.addEventListener("input", renderizarAgendaOcupacao);
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

if (formReagendar) {
    formReagendar.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idReserva = document.getElementById("reagendar-id").value;
        const payload = Object.fromEntries(new FormData(formReagendar).entries());
        try {
            const resposta = await fetch(`/api/bancadas/reservas/${idReserva}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao reagendar reserva.");
            }
            modalReagendar.close();
            if (mensagemReserva) {
                mensagemReserva.textContent = dados.mensagem;
            }
            await carregarBancadasEReservas();
        } catch (erro) {
            avisoConflitoReagendar.textContent = erro.message;
        }
    });
}

if (btnFecharReagendar) {
    btnFecharReagendar.addEventListener("click", () => modalReagendar.close());
}

carregarBancadasEReservas();
