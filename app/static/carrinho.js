const divCarrinho = document.getElementById("carrinho");
const dinheiro = valor => Number(valor).toLocaleString("pt-BR", {style:"currency", currency:"BRL"});
function obterCarrinho() { return JSON.parse(localStorage.getItem("sabor_clic_carrinho") || "[]"); }
function salvarCarrinho(itens) { localStorage.setItem("sabor_clic_carrinho", JSON.stringify(itens)); mostrarCarrinho(); }
function mostrarCarrinho() {
    const carrinho = obterCarrinho(); divCarrinho.innerHTML = "";
    let subtotal = 0;
    if (!carrinho.length) divCarrinho.textContent = "Seu carrinho está vazio.";
    carrinho.forEach(function(item, indice) {
        subtotal += item.preco * item.quantidade;
        const div = document.createElement("div"); div.className="item-carrinho";
        const titulo = document.createElement("h3"); titulo.textContent = item.nome;
        const detalhes = document.createElement("p"); detalhes.textContent = `${item.quantidade} x ${dinheiro(item.preco)}`;
        const menos = document.createElement("button"); menos.textContent = "Diminuir";
        menos.onclick = function() { alterarQuantidade(indice, -1); };
        const mais = document.createElement("button"); mais.textContent = "Aumentar";
        mais.onclick = function() { alterarQuantidade(indice, 1); };
        const remover = document.createElement("button"); remover.textContent = "Remover";
        remover.onclick = function() { salvarCarrinho(obterCarrinho().filter((i, n) => n !== indice)); };
        div.append(titulo, detalhes, menos, mais, remover); divCarrinho.appendChild(div);
    });
    document.getElementById("subtotal").textContent = `Subtotal: ${dinheiro(subtotal)}`;
    document.getElementById("finalizar").disabled = carrinho.length === 0;
}
function alterarQuantidade(indice, diferenca) {
    const carrinho = obterCarrinho(); const item = carrinho[indice];
    if (item) item.quantidade += diferenca;
    salvarCarrinho(carrinho.filter(i => i.quantidade > 0));
}
async function finalizarPedido() {
    const itens = obterCarrinho().map(item => ({prato_id:item.id, quantidade:item.quantidade, observacoes:item.observacoes||""}));
    try {
        const resposta = await fetch("/pedidos", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({itens})});
        if (resposta.redirected) { window.location.href = resposta.url; return; }
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Erro ao enviar pedido.");
        localStorage.removeItem("sabor_clic_carrinho");
        alert(`Pedido #${dados.pedido_id} realizado!`);
        window.location.href = "/pedido";
    } catch (erro) { alert(erro.message); }
}
document.getElementById("finalizar").addEventListener("click", finalizarPedido);
mostrarCarrinho();
