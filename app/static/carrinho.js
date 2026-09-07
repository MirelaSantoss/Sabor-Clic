let carrinho = []; // inicia a array do carrinho vazia

const divCarrinho = document.getElementById("carrinho"); // pega no HTML o elemento que tenha "carrinho"

function mostrarCarrinho() { // função que mostra os intem adicionados na tela no carrinho

    divCarrinho.innerHTML = ""; // Limpa o conteúdo da div antes de mostrar novamente os produtos

    let subtotal = 0; // inicia o valor do carrinho em 0

    carrinho.forEach(function(item) { // para cada item do carrinho modifica a div da página

        divCarrinho.innerHTML += `
            <div>
                <h3>${item.nome}</h3>
                <p>Preço: R$ ${item.preco.toFixed(2)}</p> // toFixed(2) - 2 valores dps da vírgula
            </div>
        `;

    }); // fim do forEach

    for (const item of carrinho) { // para cada item do carrinho, soma o preço dele ao subtotal
        subtotal += item.preco;
    }

    document.getElementById("subtotal").innerHTML = // procura no HTML o elemento que tem "subtotal" e coloca o resultado dentro dele.
        `Subtotal: R$ ${subtotal.toFixed(2)}`;
}