const kdsContainer = document.getElementById("kds");
const contadorTopo = document.getElementById("contador-kds");

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
        const pendentes = listaPedidos.filter(p => p.status !== "Entregue");

        if (contadorTopo) {
            contadorTopo.textContent = `#${pendentes.length} Pedidos a serem entregues`;
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
            cabecalhoColuna.textContent = `${tituloColuna} (${pedidosDaColuna.length})`;
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
                h3.textContent = `#${pedido.id} · ${pedido.clienteNome}`;

                const badgeTempo = document.createElement("span");
                badgeTempo.className = "pedido-kds-tempo";
                badgeTempo.textContent = `⏱ ${pedido.tempoEstimado || 20} min (${pedido.minutosDecorridos} min atrás)`;

                topoCard.append(h3, badgeTempo);
                card.append(topoCard);

                pedido.itens.forEach(item => {
                    const linha = document.createElement("p");
                    const obsItem = item.observacoes ? ` — Obs: ${item.observacoes}` : "";
                    linha.textContent = `${item.quantidade}× ${item.nome}${obsItem}`;
                    card.append(linha);
                });

                if (pedido.observacoes) {
                    const boxObs = document.createElement("div");
                    boxObs.className = "pedido-kds-obs";
                    boxObs.textContent = `📝 Observação: ${pedido.observacoes}`;
                    card.append(boxObs);
                }

                const acoes = document.createElement("div");
                acoes.className = "pedido-kds-acoes";

                const botaoTempo = document.createElement("button");
                botaoTempo.type = "button";
                botaoTempo.className = "botao-secundario";
                botaoTempo.textContent = "Definir tempo";
                botaoTempo.onclick = () => definirTempo(pedido);
                acoes.append(botaoTempo);

                if (pedido.proximoStatus) {
                    const botaoAvancar = document.createElement("button");
                    botaoAvancar.type = "button";
                    botaoAvancar.className = "botao";
                    if (statusColuna === "Aguardando") {
                        botaoAvancar.textContent = "Iniciar preparo";
                    } else if (statusColuna === "Iniciando Preparo") {
                        botaoAvancar.textContent = "Pronto para entrega";
                    } else {
                        botaoAvancar.textContent = "Concluir entrega";
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

async function definirTempo(pedido) {
    const valor = prompt("Tempo estimado de preparo (minutos):", pedido.tempoEstimado || "25");
    if (valor === null) {
        return;
    }
    const minutos = Number(valor);
    if (!Number.isInteger(minutos) || minutos < 1 || minutos > 480) {
        alert("Informe um tempo inteiro entre 1 e 480 minutos.");
        return;
    }
    try {
        const resposta = await fetch(`/pedidos/${pedido.id}/tempo`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ minutos })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Falha ao atualizar o tempo estimado.");
        }
        await mostrarPedidos();
    } catch (erro) {
        alert(erro.message);
    }
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
