const divCarrinho = document.getElementById("carrinho");
const elementoSubtotal = document.getElementById("subtotal");
const botaoFinalizar = document.getElementById("finalizar");
const modalObsCarrinho = document.getElementById("modal-obs-carrinho");
const formObsCarrinho = document.getElementById("form-obs-carrinho");
const btnFecharObsCarrinho = document.getElementById("fechar-obs-carrinho");

const carrinho = new Carrinho();

function abrirModalObservacaoItem(indice, item) {
    if (!modalObsCarrinho) {
        return;
    }
    document.getElementById("indice-obs-carrinho").value = String(indice);
    document.getElementById("titulo-obs-carrinho").textContent = `Observações — ${item.nome}`;
    document.getElementById("texto-obs-carrinho").value = item.observacoes || "";
    modalObsCarrinho.showModal();
}

function mostrarCarrinho() {
    carrinho.carregar();
    divCarrinho.replaceChildren();

    if (carrinho.vazio) {
        divCarrinho.textContent = "Seu carrinho está vazio.";
    }

    carrinho.itens.forEach((item, indice) => {
        const container = document.createElement("div");
        container.className = "item-carrinho";

        const infoContainer = document.createElement("div");
        infoContainer.style.flex = "1";

        const titulo = document.createElement("h3");
        titulo.textContent = item.nome;
        infoContainer.append(titulo);

        const obs = document.createElement("small");
        obs.textContent = item.observacoes ? `Obs.: ${item.observacoes}` : "Sem observações adicionadas.";
        infoContainer.append(obs);

        const detalhes = document.createElement("p");
        detalhes.textContent = `${item.quantidade} × ${Prato.formatarMoeda(item.preco)} = ${item.subtotalFormatado}`;

        const botaoEditarObs = document.createElement("button");
        botaoEditarObs.type = "button";
        botaoEditarObs.textContent = "Editar obs.";
        botaoEditarObs.onclick = () => abrirModalObservacaoItem(indice, item);

        const botaoMenos = document.createElement("button");
        botaoMenos.type = "button";
        botaoMenos.textContent = "Diminuir";
        botaoMenos.onclick = () => {
            carrinho.alterarQuantidade(indice, -1);
            mostrarCarrinho();
        };

        const botaoMais = document.createElement("button");
        botaoMais.type = "button";
        botaoMais.textContent = "Aumentar";
        botaoMais.onclick = () => {
            carrinho.alterarQuantidade(indice, 1);
            mostrarCarrinho();
        };

        const botaoRemover = document.createElement("button");
        botaoRemover.type = "button";
        botaoRemover.textContent = "Remover";
        botaoRemover.onclick = () => {
            carrinho.remover(indice);
            mostrarCarrinho();
        };

        container.append(infoContainer, detalhes, botaoEditarObs, botaoMenos, botaoMais, botaoRemover);
        divCarrinho.appendChild(container);
    });

    elementoSubtotal.textContent = `Subtotal: ${carrinho.subtotalFormatado}`;
    botaoFinalizar.disabled = carrinho.vazio;
}

if (formObsCarrinho) {
    formObsCarrinho.addEventListener("submit", evento => {
        evento.preventDefault();
        const indice = Number(document.getElementById("indice-obs-carrinho").value);
        const texto = document.getElementById("texto-obs-carrinho").value;
        carrinho.atualizarObservacoes(indice, texto);
        modalObsCarrinho.close();
        mostrarCarrinho();
    });
}

if (btnFecharObsCarrinho) {
    btnFecharObsCarrinho.addEventListener("click", () => modalObsCarrinho.close());
}

async function finalizarPedido() {
    carrinho.carregar();
    if (carrinho.vazio) {
        return;
    }

    botaoFinalizar.disabled = true;
    const textoOriginal = botaoFinalizar.textContent;
    botaoFinalizar.textContent = "Enviando pedido...";

    try {
        const resposta = await fetch("/pedidos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(carrinho.paraPayload())
        });

        if (resposta.redirected) {
            window.location.href = resposta.url;
            return;
        }

        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao enviar pedido.");
        }

        carrinho.limpar();
        alert(`Pedido #${dados.pedido_id} realizado com sucesso!`);
        window.location.href = "/pedido";
    } catch (erro) {
        alert(erro.message);
        botaoFinalizar.disabled = false;
        botaoFinalizar.textContent = textoOriginal;
    }
}

botaoFinalizar.addEventListener("click", finalizarPedido);
mostrarCarrinho();
