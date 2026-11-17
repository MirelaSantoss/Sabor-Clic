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
            const cardVazio = document.createElement("div");
            cardVazio.className = "form-card";
            cardVazio.textContent = "Você ainda não realizou pedidos.";
            containerPedidos.appendChild(cardVazio);
            return;
        }

        pedidos.forEach(pedido => {
            const card = document.createElement("article");
            card.className = "item-carrinho card-pedido-cliente";

            const bloco = document.createElement("div");
            bloco.className = "info-prato-admin";
            bloco.style.flex = "1";

            const topo = document.createElement("div");
            topo.className = "produto-horizontal-topo";

            const titulo = document.createElement("h3");
            titulo.textContent = `Pedido #${pedido.id}`;

            const badgeStatus = document.createElement("span");
            badgeStatus.className = pedido.status === "Cancelado" ? "badge-alerta" : "badge-normal";
            badgeStatus.textContent = pedido.status;

            topo.append(titulo, badgeStatus);

            const descricaoItens = pedido.itens
                .map(i => {
                    const obs = i.observacoes ? ` [${i.observacoes}]` : "";
                    return `${i.quantidade}× ${i.nome}${obs}`;
                })
                .join(" · ");

            const paragrafoItens = document.createElement("p");
            paragrafoItens.textContent = `Itens: ${descricaoItens}`;

            const meta = document.createElement("small");
            const textoTempo = pedido.tempoEstimado ? ` · Preparo estimado: ${pedido.tempoEstimado} min` : "";
            meta.textContent = `Realizado em: ${pedido.dataPedido}${textoTempo}`;

            bloco.append(topo, paragrafoItens, meta);

            if (pedido.observacoes) {
                const paragrafoObs = document.createElement("div");
                paragrafoObs.className = "pedido-kds-obs icone-inline";
                paragrafoObs.append(
                    Icones.criar("note", "icone-svg-sm"),
                    document.createTextNode(`Observações: ${pedido.observacoes}`)
                );
                bloco.append(paragrafoObs);
            }

            const paragrafoTotal = document.createElement("strong");
            paragrafoTotal.className = "valor-preco-pilula";
            paragrafoTotal.textContent = `Total: ${pedido.totalFormatado}`;

            card.append(bloco, paragrafoTotal);
            containerPedidos.appendChild(card);
        });
    } catch (erro) {
        containerPedidos.textContent = erro.message;
    }
}

carregarPedidosCliente();
