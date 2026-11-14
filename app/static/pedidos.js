const meusPedidos = document.getElementById("meus-pedidos");
async function mostrarPedidos() {
    try {
        const resposta = await fetch("/pedidos");
        const pedidos = await resposta.json();
        if (!resposta.ok) throw new Error(pedidos.erro || "Erro ao carregar pedidos.");
        meusPedidos.innerHTML = "";
        if (!pedidos.length) meusPedidos.textContent = "Você ainda não fez pedidos.";
        pedidos.forEach(function(pedido) {
            const div = document.createElement("div");
            const titulo = document.createElement("h3"); titulo.textContent = `Pedido #${pedido.id}`;
            const itens = document.createElement("p"); itens.textContent = "Itens: " + (pedido.itens || []).map(i => `${i.nome} (${i.quantidade})`).join(", ");
            const status = document.createElement("p"); status.textContent = `Status: ${pedido.status}`;
            const total = document.createElement("p"); total.textContent = `Total: R$ ${Number(pedido.total).toFixed(2)}`;
            div.append(titulo, itens, status, total); meusPedidos.appendChild(div);
        });
    } catch (erro) { meusPedidos.textContent = erro.message; }
}
mostrarPedidos();
