const containerPedidos = document.getElementById("meus-pedidos");

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

carregarPedidosCliente();
