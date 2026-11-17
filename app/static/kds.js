const kdsContainer = document.getElementById("kds");
const contadorTopo = document.getElementById("contador-kds");
const modalTempoKds = document.getElementById("modal-tempo-kds");
const formTempoKds = document.getElementById("form-tempo-kds");
const btnFecharModalKds = document.getElementById("fechar-modal-kds");

const COLUNAS_KDS = [
    ["Aguardando", "Pedidos Novos"],
    ["Iniciando Preparo", "Pedidos em Andamento"],
    ["Pronto para Entrega", "Prontos para Entrega"]
];

async function mostrarPedidos() {
    try {
        const resposta = await fetch("/api/pedidos/fila");
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Falha ao carregar fila de pedidos.");
        }

        const listaPedidos = dados.map(item => new Pedido(item));
        const pendentes = listaPedidos.filter(p => !["Entregue", "Cancelado"].includes(p.status));

        if (contadorTopo) {
            contadorTopo.textContent = `#${pendentes.length}  Pedidos a serem entregues`;
        }

        kdsContainer.replaceChildren();

        COLUNAS_KDS.forEach(([statusColuna, tituloColuna]) => {
            const pedidosDaColuna = listaPedidos.filter(p => p.status === statusColuna);

            const coluna = document.createElement("section");
            coluna.className = "kds-coluna";
            coluna.dataset.status = statusColuna;

            coluna.addEventListener("dragover", evento => {
                evento.preventDefault();
                coluna.classList.add("kds-coluna-alvo");
            });

            coluna.addEventListener("dragleave", () => {
                coluna.classList.remove("kds-coluna-alvo");
            });

            coluna.addEventListener("drop", async evento => {
                evento.preventDefault();
                coluna.classList.remove("kds-coluna-alvo");
                const idArrastado = Number(evento.dataTransfer.getData("text/plain"));
                if (idArrastado) {
                    await alterarStatusDireto(idArrastado, statusColuna);
                }
            });

            const cabecalhoColuna = document.createElement("h2");
            const spanTitulo = document.createElement("span");
            spanTitulo.textContent = tituloColuna;
            const spanQtdColuna = document.createElement("span");
            spanQtdColuna.className = "kds-contador-coluna";
            spanQtdColuna.textContent = String(pedidosDaColuna.length).padStart(2, "0");
            cabecalhoColuna.append(spanTitulo, spanQtdColuna);
            coluna.append(cabecalhoColuna);

            pedidosDaColuna.forEach(pedido => {
                const card = document.createElement("article");
                card.className = "pedido-kds";
                card.draggable = true;

                card.addEventListener("dragstart", evento => {
                    evento.dataTransfer.setData("text/plain", String(pedido.id));
                });

                const topoCard = document.createElement("div");
                topoCard.className = "pedido-kds-topo";

                const h3 = document.createElement("h3");
                const idFormatado = String(pedido.id).padStart(4, "0");
                h3.textContent = `#${idFormatado}`;
                h3.title = `Cliente: ${pedido.clienteNome}`;

                const blocoCronometro = document.createElement("div");
                blocoCronometro.className = "kds-bloco-cronometro";

                const iconeTimer = document.createElement("span");
                iconeTimer.className = "kds-icone-timer-card";
                iconeTimer.setAttribute("aria-hidden", "true");
                iconeTimer.append(Icones.criar("clock"));

                const badgeTempo = document.createElement("span");
                badgeTempo.className = "pedido-kds-tempo";
                badgeTempo.textContent = `${pedido.tempoEstimado || 20} min`;
                badgeTempo.onclick = () => abrirModalTempoKds(pedido);

                blocoCronometro.append(iconeTimer, badgeTempo);
                topoCard.append(h3, blocoCronometro);
                card.append(topoCard);

                const listaItens = document.createElement("div");
                listaItens.className = "kds-lista-itens";

                pedido.itens.forEach(item => {
                    const linha = document.createElement("div");
                    linha.className = "kds-linha-item";

                    const boxQtd = document.createElement("span");
                    boxQtd.className = "kds-qtd-box";
                    boxQtd.textContent = `${item.quantidade}x`;

                    const nomePrato = document.createElement("strong");
                    nomePrato.className = "kds-nome-prato";
                    const obsItem = item.observacoes ? ` (${item.observacoes})` : "";
                    nomePrato.textContent = `${item.nome}${obsItem}`;

                    const tagCat = document.createElement("span");
                    tagCat.className = "kds-tag-categoria";
                    tagCat.textContent = item.categoria || "Pratos";

                    linha.append(boxQtd, nomePrato, tagCat);
                    listaItens.append(linha);
                });

                card.append(listaItens);

                const boxObs = document.createElement("div");
                boxObs.className = pedido.observacoes
                    ? "kds-barra-observacao com-obs"
                    : "kds-barra-observacao";
                boxObs.onclick = () => abrirModalTempoKds(pedido);

                const iconeNota = document.createElement("span");
                iconeNota.setAttribute("aria-hidden", "true");
                iconeNota.append(Icones.criar("note"));

                const textoObs = document.createElement("span");
                textoObs.textContent = pedido.observacoes
                    ? `Observação: ${pedido.observacoes}`
                    : "Observação (clique para editar tempo / nota)";

                boxObs.append(iconeNota, textoObs);
                card.append(boxObs);

                const acoes = document.createElement("div");
                acoes.className = "pedido-kds-acoes";

                const botaoTempo = document.createElement("button");
                botaoTempo.type = "button";
                botaoTempo.className = "botao-secundario";
                botaoTempo.textContent = "Tempo / Obs.";
                botaoTempo.onclick = () => abrirModalTempoKds(pedido);
                acoes.append(botaoTempo);

                if (pedido.proximoStatus) {
                    const botaoAvancar = document.createElement("button");
                    botaoAvancar.type = "button";
                    botaoAvancar.className = "botao";
                    if (statusColuna === "Aguardando") {
                        botaoAvancar.textContent = "Iniciar preparo →";
                    } else if (statusColuna === "Iniciando Preparo") {
                        botaoAvancar.textContent = "Pronto p/ entrega →";
                    } else {
                        Icones.preencher(botaoAvancar, "check", "Concluir entrega");
                    }
                    botaoAvancar.onclick = () => alterarStatusDireto(pedido.id, pedido.proximoStatus);
                    acoes.append(botaoAvancar);
                }

                card.append(acoes);
                coluna.append(card);
            });

            kdsContainer.append(coluna);
        });
    } catch (erro) {
        kdsContainer.textContent = erro.message;
    }
}

async function alterarStatusDireto(idPedido, novoStatus) {
    try {
        const resposta = await fetch(`/pedidos/${idPedido}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: novoStatus })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Não foi possível alterar o status do pedido.");
        }
        await mostrarPedidos();
    } catch (erro) {
        alert(erro.message);
    }
}

function abrirModalTempoKds(pedido) {
    if (!modalTempoKds) {
        return;
    }
    document.getElementById("kds-pedido-id").value = pedido.id;
    document.getElementById("titulo-modal-kds").textContent = `Comanda #${String(pedido.id).padStart(4, "0")} (${pedido.clienteNome})`;
    document.getElementById("kds-input-minutos").value = pedido.tempoEstimado || 25;
    document.getElementById("kds-input-observacoes").value = pedido.observacoes || "";
    modalTempoKds.showModal();
}

document.querySelectorAll(".preset-tempo").forEach(botao => {
    botao.addEventListener("click", () => {
        document.getElementById("kds-input-minutos").value = botao.dataset.min;
    });
});

if (formTempoKds) {
    formTempoKds.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idPedido = document.getElementById("kds-pedido-id").value;
        const minutos = Number(document.getElementById("kds-input-minutos").value);
        const observacoes = document.getElementById("kds-input-observacoes").value;
        try {
            const resposta = await fetch(`/pedidos/${idPedido}/tempo`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ minutos, observacoes })
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Falha ao atualizar o tempo estimado.");
            }
            modalTempoKds.close();
            await mostrarPedidos();
        } catch (erro) {
            alert(erro.message);
        }
    });
}

if (btnFecharModalKds) {
    btnFecharModalKds.addEventListener("click", () => modalTempoKds.close());
}

function atualizarRelogio() {
    const elementoRelogio = document.getElementById("relogio");
    if (elementoRelogio) {
        elementoRelogio.textContent = new Date().toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit"
        });
    }
}

atualizarRelogio();
setInterval(atualizarRelogio, 30000);
mostrarPedidos();
setInterval(mostrarPedidos, 15000);
