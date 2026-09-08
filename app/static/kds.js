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

const kds = document.getElementById("kds"); // procura no HTML elemento que tenha kds

pedidos.forEach(function(pedido){ //para cada pedido da array cria uma div com as informações
    kds.innerHTML += `
        <div>
            <h2>Pedido #${pedido.id}</h2>
            <p>Cliente: ${pedido.cliente}</p>
            <p>Itens: ${pedido.itens}</p>
            <p>Status: ${pedido.status}</p>

            <button onclick="alterarStatus(${pedido.id})"> //botão que dispara a função para criar status
                Alterar status
            </button>
        </div>
    `;
        
});

function alterarStatus(id) { //função acionada pelo botão alternar status

    const pedido_encontrado = pedidos.find(function(pedido) { // procura o pedidio dentro da array e coloca no pedido_encontrado
        return pedido.id === id; // verifica e id do pedido é igual ao id da função
    });

    if (pedido_encontrado.status === "Em preparo") { // se o status for em preparo ao apertar vira saiu para entrega
        pedido_encontrado.status = "Saiu para entrega";
    } 
    else if (pedido_encontrado.status === "Saiu para entrega") { // se o status for saiu para entrega ao apertar vira entregue
        pedido_encontrado.status = "Entregue";
    }

    mostrarPedidos();
}

