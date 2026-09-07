const pratos = [
    {
        id: 1,
        nome: "Hambúrguer com frango",
        descricao: "Hambúrguer com queijo e bacon",
        preco: 40.00
    },

    {
        id: 2,
        nome: "Marmitex simples",
        descricao: "Arroz e Feijão com strogonoff de frango",
        preco: 27.90
    },

    {
        id: 3,
        nome: "Super marmitex",
        descricao: "Arroz e Feijão acompanhado com lasanha, batata frita e salada",
        preco: 40.00
    }
];

const cardapio = document.getElementById("cardapio");

pratos.forEach(function(prato) {

    cardapio.innerHTML += `
        <div>
            <h2>${prato.nome}</h2>
            <p>${prato.descricao}</p>
            <p>R$ ${prato.preco}</p>

            <button onclick="adicionarCarrinho(${prato.id})">
                Adicionar ao carrinho
            </button>
        </div>
    `;

});

let carrinho = [];

function adicionarCarrinho(id) { // função que é acionada no botão acima, ela adiciona oas pratos no carrinho

    const prato = pratos.find(function(prato) { // procura na array o prato e compara ele com o id inicial
        return prato.id === id;
    });

    carrinho.push(prato); //adiciona o prato escolhido no carrinho

    console.log(carrinho); // mostra no console o que está no carrinho (opcional)
}