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

pratos.forEach(function(prato){
    <div>
        <h2>${prato.nome}</h2>
        <p>${prato.descricao}</p>
        <p>R$ ${prato.preco}</p>
    </div>
})



