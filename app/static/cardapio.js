const cardapioContainer = document.getElementById("cardapio");
const campoPesquisa = document.getElementById("pesquisa");
const modalDetalhes = document.getElementById("detalhes");
const corpoDetalhes = document.getElementById("detalhes-corpo");
const botaoFecharDetalhes = document.getElementById("fechar-detalhes");

const CATEGORIAS_MENU = ["Pratos", "Bebidas", "Combos", "Sobremesas"];
const gerenciadorCarrinho = new Carrinho();
let listaPratos = [];

async function carregarCardapio() {
    cardapioContainer.textContent = "Carregando cardápio...";
    try {
        const resposta = await fetch("/api/pratos");
        if (!resposta.ok) {
            throw new Error("Erro ao carregar o cardápio.");
        }
        const dados = await resposta.json();
        listaPratos = dados.map(item => new Prato(item));
        renderizarCardapio();
    } catch (erro) {
        cardapioContainer.textContent = erro.message;
    }
}

function renderizarCardapio() {
    const termoBusca = campoPesquisa ? campoPesquisa.value : "";
    cardapioContainer.replaceChildren();

    for (const categoria of CATEGORIAS_MENU) {
        const itensCategoria = listaPratos.filter(
            prato => prato.categoria === categoria && prato.correspondeBusca(termoBusca)
        );

        const secao = document.createElement("section");
        secao.id = categoria;

        const tituloSecao = document.createElement("h2");
        tituloSecao.textContent = categoria;
        secao.append(tituloSecao);

        const grade = document.createElement("div");
        grade.className = "grade-produtos";

        itensCategoria.forEach(prato => {
            const card = document.createElement("article");
            card.className = "produto";

            if (prato.imagem) {
                const img = document.createElement("img");
                img.src = `/static/${prato.imagem}`;
                img.alt = prato.nome;
                card.append(img);
            } else {
                const placeholder = document.createElement("div");
                placeholder.className = "foto-vazia";
                placeholder.textContent = "🍽";
                card.append(placeholder);
            }

            const titulo = document.createElement("h3");
            titulo.textContent = prato.nome;

            const descricao = document.createElement("p");
            descricao.textContent = prato.descricao;

            const preco = document.createElement("strong");
            preco.textContent = prato.precoFormatado;

            const botao = document.createElement("button");
            botao.className = "botao";
            botao.type = "button";
            botao.textContent = "Ver detalhes";
            botao.onclick = () => abrirDetalhes(prato);

            card.append(titulo, descricao, preco, botao);
            grade.append(card);
        });

        if (itensCategoria.length === 0) {
            const avisoVazio = document.createElement("p");
            avisoVazio.textContent = "Nenhum produto nesta categoria.";
            grade.append(avisoVazio);
        }

        secao.append(grade);
        cardapioContainer.append(secao);
    }
}

function abrirDetalhes(prato) {
    corpoDetalhes.replaceChildren();

    const titulo = document.createElement("h2");
    titulo.textContent = prato.nome;

    const descricao = document.createElement("p");
    descricao.textContent = prato.descricao;

    const preco = document.createElement("strong");
    preco.textContent = prato.precoFormatado;

    const rotuloQtd = document.createElement("label");
    rotuloQtd.textContent = "Quantidade";
    const inputQuantidade = document.createElement("input");
    inputQuantidade.type = "number";
    inputQuantidade.min = "1";
    inputQuantidade.step = "1";
    inputQuantidade.value = "1";
    rotuloQtd.append(inputQuantidade);

    const rotuloObs = document.createElement("label");
    rotuloObs.textContent = "Observações";
    const campoObservacoes = document.createElement("textarea");
    campoObservacoes.placeholder = "Ex.: sem cebola, ponto da carne (opcional)";
    rotuloObs.append(campoObservacoes);

    const botaoAdicionar = document.createElement("button");
    botaoAdicionar.className = "botao";
    botaoAdicionar.type = "button";
    botaoAdicionar.textContent = "Adicionar ao carrinho";
    botaoAdicionar.onclick = () => {
        const adicionou = adicionarAoCarrinho(
            prato,
            Number(inputQuantidade.value),
            campoObservacoes.value
        );
        if (adicionou) {
            modalDetalhes.close();
        }
    };

    corpoDetalhes.append(titulo, descricao, preco, rotuloQtd, rotuloObs, botaoAdicionar);
    modalDetalhes.showModal();
}

function adicionarAoCarrinho(prato, quantidade, observacoes) {
    try {
        gerenciadorCarrinho.carregar();
        gerenciadorCarrinho.adicionar(prato, quantidade, observacoes);
        alert("Produto adicionado ao carrinho!");
        return true;
    } catch (erro) {
        alert(erro.message || "Quantidade inválida.");
        return false;
    }
}

if (campoPesquisa) {
    campoPesquisa.addEventListener("input", renderizarCardapio);
}

if (botaoFecharDetalhes) {
    botaoFecharDetalhes.onclick = () => modalDetalhes.close();
}

carregarCardapio();
