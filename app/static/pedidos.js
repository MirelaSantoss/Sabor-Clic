const pedidos = [ //array temporaria de pedidos
    {
        id: 1,
        cliente: "Mirela",
        itens: ["Hambueguer de frango"],
        status: "Em preparo"
    },
    {
        id: 2,
        cliente: "Lorena",
        itens: ["Marmitex simples"],
        status: "Saiu para entrega"
    },

    {
        id: 3,
        cliente: "Luis",
        itens: ["Super marmitex"],
        status: "Entregue"
    }
];

const cliente_atual = "Mirela"; 

const meusPedidos = document.getElementById("meus-pedidos")

pedidos.forEach(function(pedido){
    if (pedido.cliente === cliente_atual){
        meusPedidos.innerHTML += `
            <div>
                <h3>Pedido #${pedido.id}</h3>
                <p>Itens: ${pedido.itens}</p>
                <p>Status: ${pedido.status}</p>
            </div>
        `;
    }
});

