const divCarrinho = document.getElementById("carrinho");
const elementoSubtotal = document.getElementById("subtotal");
const botaoFinalizar = document.getElementById("finalizar");
const botaoLimparCarrinho = document.getElementById("limpar-carrinho");
const modalObsCarrinho = document.getElementById("modal-obs-carrinho");
const formObsCarrinho = document.getElementById("form-obs-carrinho");
const btnFecharObsCarrinho = document.getElementById("fechar-obs-carrinho");
const resumoItemObs = document.getElementById("resumo-item-obs-carrinho");

const carrinho = new Carrinho();

function abrirModalObservacaoItem(indice, item) {
    if (!modalObsCarrinho) {
        return;
    }
    document.getElementById("indice-obs-carrinho").value = String(indice);
    document.getElementById("titulo-obs-carrinho").textContent = `Detalhes — ${item.nome}`;
    if (resumoItemObs) {
        resumoItemObs.textContent = `Quantidade: ${item.quantidade} × ${Prato.formatarMoeda(item.preco)} (${item.subtotalFormatado})`;
    }
    document.getElementById("texto-obs-carrinho").value = item.observacoes || "";
    modalObsCarrinho.showModal();
}

function mostrarCarrinho() {
    carrinho.carregar();
    divCarrinho.replaceChildren();

    if (carrinho.vazio) {
        const vazioCard = document.createElement("div");
        vazioCard.className = "form-card";
        vazioCard.textContent = "Seu carrinho está vazio. Clique em 'Adicionar Item' para explorar o cardápio.";
        divCarrinho.appendChild(vazioCard);
    }

    carrinho.itens.forEach((item, indice) => {
        const container = document.createElement("article");
        container.className = "item-carrinho item-carrinho-figma";

        const fotoBox = document.createElement("div");
        fotoBox.className = "foto-item-carrinho";
        if (item.imagem) {
            const img = document.createElement("img");
            img.src = `/static/${item.imagem}`;
            img.alt = item.nome;
            fotoBox.append(img);
        } else {
            fotoBox.append(Icones.criar("utensils", "icone-svg-lg"));
        }

        const infoContainer = document.createElement("div");
        infoContainer.className = "info-item-carrinho";

        const titulo = document.createElement("h3");
        titulo.textContent = item.nome;

        const linhaSub = document.createElement("div");
        linhaSub.className = "linha-preco-obs-carrinho";

        const precoTxt = document.createElement("strong");
        precoTxt.textContent = `${Prato.formatarMoeda(item.preco)} (Subtotal: ${item.subtotalFormatado})`;

        const botaoEditarObs = document.createElement("button");
        botaoEditarObs.type = "button";
        botaoEditarObs.className = "btn-ver-descricao-carrinho";
        botaoEditarObs.textContent = "Ver descrição / Editar obs.";
        botaoEditarObs.onclick = () => abrirModalObservacaoItem(indice, item);

        linhaSub.append(precoTxt, botaoEditarObs);

        const obs = document.createElement("small");
        obs.textContent = item.observacoes ? `Observação: ${item.observacoes}` : "Sem observações especiais.";

        infoContainer.append(titulo, linhaSub, obs);

        const blocoQtd = document.createElement("div");
        blocoQtd.className = "qtd-item-carrinho";

        const rotuloQtd = document.createElement("strong");
        rotuloQtd.textContent = "Quantidade:";

        const controle = document.createElement("div");
        controle.className = "controle-qtd";

        const botaoMenos = document.createElement("button");
        botaoMenos.type = "button";
        botaoMenos.textContent = "−";
        botaoMenos.onclick = () => {
            carrinho.alterarQuantidade(indice, -1);
            mostrarCarrinho();
        };

        const spanQtd = document.createElement("span");
        spanQtd.textContent = String(item.quantidade);

        const botaoMais = document.createElement("button");
        botaoMais.type = "button";
        botaoMais.textContent = "+";
        botaoMais.onclick = () => {
            carrinho.alterarQuantidade(indice, 1);
            mostrarCarrinho();
        };

        controle.append(botaoMenos, spanQtd, botaoMais);

        const botaoRemover = document.createElement("button");
        botaoRemover.type = "button";
        botaoRemover.className = "botao-secundario";
        botaoRemover.textContent = "Remover";
        botaoRemover.onclick = () => {
            carrinho.remover(indice);
            mostrarCarrinho();
        };

        blocoQtd.append(rotuloQtd, controle, botaoRemover);

        container.append(fotoBox, infoContainer, blocoQtd);
        divCarrinho.appendChild(container);
    });

    elementoSubtotal.textContent = `Valor total: ${carrinho.subtotalFormatado}`;
    botaoFinalizar.disabled = carrinho.vazio;
    if (botaoLimparCarrinho) {
        botaoLimparCarrinho.disabled = carrinho.vazio;
    }
}

if (botaoLimparCarrinho) {
    botaoLimparCarrinho.addEventListener("click", () => {
        carrinho.limpar();
        mostrarCarrinho();
    });
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
        window.location.href = "/pedido";
    } catch (erro) {
        alert(erro.message);
        botaoFinalizar.disabled = false;
        mostrarCarrinho();
    }
}

botaoFinalizar.addEventListener("click", finalizarPedido);
mostrarCarrinho();
