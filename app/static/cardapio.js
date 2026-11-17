const cardapioContainer = document.getElementById("cardapio");
const campoPesquisa = document.getElementById("pesquisa");
const botaoLimparPesquisa = document.getElementById("limpar-pesquisa");
const modalDetalhes = document.getElementById("detalhes");
const corpoDetalhes = document.getElementById("detalhes-corpo");
const tituloModalDetalhes = document.getElementById("detalhes-titulo-modal");
const botaoFecharDetalhes = document.getElementById("fechar-detalhes");

const modalConfirmacao = document.getElementById("modal-confirmacao-adicao");
const confTituloProduto = document.getElementById("conf-titulo-produto");
const confQuantidadeProduto = document.getElementById("conf-quantidade-produto");
const confObservacoesProduto = document.getElementById("conf-observacoes-produto");
const btnConfVoltar = document.getElementById("btn-conf-voltar");

const CATEGORIAS_MENU = ["Pratos", "Bebidas", "Combos", "Sobremesas"];
const TITULOS_DETALHE = {
    Pratos: "Detalhes do prato",
    Bebidas: "Detalhes da bebida",
    Combos: "Detalhes do combo",
    Sobremesas: "Detalhes da sobremesa"
};

const gerenciadorCarrinho = new Carrinho();
let listaPratos = [];

function configurarLinksCategoria() {
    const links = document.querySelectorAll(".link-categoria");
    links.forEach(link => {
        link.addEventListener("click", () => {
            links.forEach(l => l.classList.toggle("ativa", l === link));
        });
    });
}

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
        secao.className = "secao-categoria-cardapio";

        const tituloSecao = document.createElement("h2");
        tituloSecao.textContent = `${categoria}:`;
        secao.append(tituloSecao);

        const listaHorizontal = document.createElement("div");
        listaHorizontal.className = "lista-produtos-figma";

        itensCategoria.forEach(prato => {
            const card = document.createElement("article");
            card.className = "produto-horizontal";

            const colunaInfo = document.createElement("div");
            colunaInfo.className = "produto-horizontal-info";

            const cabecalhoItem = document.createElement("div");
            cabecalhoItem.className = "produto-horizontal-topo";

            const titulo = document.createElement("h3");
            titulo.textContent = prato.nome;

            const tempoTag = document.createElement("small");
            tempoTag.className = "tag-tempo-cardapio";
            tempoTag.textContent = `⏱ ~${prato.tempoPreparoMin} min`;

            cabecalhoItem.append(titulo, tempoTag);

            const pilulaDescPreco = document.createElement("div");
            pilulaDescPreco.className = "pilula-descricao-preco";

            const descricao = document.createElement("span");
            descricao.className = "texto-descricao-pilula";
            descricao.textContent = prato.descricao;

            const pontilhado = document.createElement("span");
            pontilhado.className = "pontilhado-preco";
            pontilhado.setAttribute("aria-hidden", "true");

            const preco = document.createElement("strong");
            preco.className = "valor-preco-pilula";
            preco.textContent = prato.precoFormatado;

            pilulaDescPreco.append(descricao, pontilhado, preco);

            const acoesCard = document.createElement("div");
            acoesCard.className = "acoes-produto-horizontal";

            const botao = document.createElement("button");
            botao.className = "botao";
            botao.type = "button";
            botao.textContent = "Ver detalhes / Adicionar";
            botao.onclick = () => abrirDetalhes(prato);

            acoesCard.append(botao);
            colunaInfo.append(cabecalhoItem, pilulaDescPreco, acoesCard);

            const colunaFoto = document.createElement("div");
            colunaFoto.className = "produto-horizontal-foto";
            colunaFoto.onclick = () => abrirDetalhes(prato);

            if (prato.imagem) {
                const img = document.createElement("img");
                img.src = `/static/${prato.imagem}`;
                img.alt = prato.nome;
                colunaFoto.append(img);
            } else {
                const placeholder = document.createElement("div");
                placeholder.className = "foto-vazia-horizontal";
                placeholder.textContent = "🍽";
                colunaFoto.append(placeholder);
            }

            card.append(colunaInfo, colunaFoto);
            listaHorizontal.append(card);
        });

        if (itensCategoria.length === 0) {
            const avisoVazio = document.createElement("p");
            avisoVazio.textContent = "Nenhum produto encontrado nesta categoria.";
            listaHorizontal.append(avisoVazio);
        }

        secao.append(listaHorizontal);
        cardapioContainer.append(secao);
    }
}

function abrirDetalhes(prato) {
    corpoDetalhes.replaceChildren();

    if (tituloModalDetalhes) {
        tituloModalDetalhes.textContent = TITULOS_DETALHE[prato.categoria] || "Detalhes do prato";
    }

    const gradePrincipal = document.createElement("div");
    gradePrincipal.className = "detalhes-grade-figma";

    const caixaFoto = document.createElement("div");
    caixaFoto.className = "detalhes-foto-grande";
    if (prato.imagem) {
        const img = document.createElement("img");
        img.src = `/static/${prato.imagem}`;
        img.alt = prato.nome;
        caixaFoto.append(img);
    } else {
        const icone = document.createElement("span");
        icone.textContent = "🍽";
        caixaFoto.append(icone);
    }

    const caixaTexto = document.createElement("div");
    caixaTexto.className = "detalhes-texto-figma";

    const titulo = document.createElement("h3");
    titulo.textContent = prato.nome;

    const precoUnitario = document.createElement("strong");
    precoUnitario.className = "detalhes-preco-destaque";
    precoUnitario.textContent = `${prato.precoFormatado} · Preparo estimado: ${prato.tempoPreparoMin} min`;

    const descricao = document.createElement("p");
    descricao.textContent = prato.descricao;

    caixaTexto.append(titulo, precoUnitario, descricao);
    gradePrincipal.append(caixaFoto, caixaTexto);

    const caixaObs = document.createElement("div");
    caixaObs.className = "detalhes-obs-box";

    const rotuloObs = document.createElement("label");
    rotuloObs.textContent = "Observações:";
    const campoObservacoes = document.createElement("textarea");
    campoObservacoes.placeholder = "Exemplo: Tirar a cebola, ponto da carne ou talheres descartáveis (opcional)";
    rotuloObs.append(campoObservacoes);
    caixaObs.append(rotuloObs);

    const barraInferior = document.createElement("div");
    barraInferior.className = "detalhes-barra-inferior";

    const blocoQtd = document.createElement("div");
    blocoQtd.className = "detalhes-bloco-qtd";

    const labelQtd = document.createElement("strong");
    labelQtd.textContent = "Quantidade:";

    const controleQtd = document.createElement("div");
    controleQtd.className = "controle-qtd";

    let qtdAtual = 1;
    const spanValorQtd = document.createElement("span");
    spanValorQtd.textContent = "1";

    const botaoAdicionar = document.createElement("button");
    botaoAdicionar.className = "botao botao-adicionar-detalhes";
    botaoAdicionar.type = "button";

    const atualizarTextoBotao = () => {
        spanValorQtd.textContent = String(qtdAtual);
        const subtotal = prato.preco * qtdAtual;
        botaoAdicionar.textContent = `🛒 Adicionar ao carrinho: ${Prato.formatarMoeda(subtotal)}`;
    };

    const btnMenos = document.createElement("button");
    btnMenos.type = "button";
    btnMenos.textContent = "−";
    btnMenos.onclick = () => {
        if (qtdAtual > 1) {
            qtdAtual -= 1;
            atualizarTextoBotao();
        }
    };

    const btnMais = document.createElement("button");
    btnMais.type = "button";
    btnMais.textContent = "+";
    btnMais.onclick = () => {
        qtdAtual += 1;
        atualizarTextoBotao();
    };

    controleQtd.append(btnMenos, spanValorQtd, btnMais);
    blocoQtd.append(labelQtd, controleQtd);

    atualizarTextoBotao();

    botaoAdicionar.onclick = () => {
        const obsTexto = campoObservacoes.value.trim();
        const adicionou = adicionarAoCarrinho(prato, qtdAtual, obsTexto);
        if (adicionou) {
            modalDetalhes.close();
            abrirModalConfirmacao(prato, qtdAtual, obsTexto);
        }
    };

    barraInferior.append(blocoQtd, botaoAdicionar);

    corpoDetalhes.append(gradePrincipal, caixaObs, barraInferior);
    modalDetalhes.showModal();
}

function abrirModalConfirmacao(prato, quantidade, observacoes) {
    if (!modalConfirmacao) {
        return;
    }
    if (confTituloProduto) {
        confTituloProduto.textContent = `${prato.nome} foi adicionado ao carrinho`;
    }
    if (confQuantidadeProduto) {
        confQuantidadeProduto.textContent = `Quantidade: ${quantidade} (${Prato.formatarMoeda(prato.preco * quantidade)})`;
    }
    if (confObservacoesProduto) {
        confObservacoesProduto.textContent = observacoes || "Nenhuma observação adicionada.";
    }
    modalConfirmacao.showModal();
}

function adicionarAoCarrinho(prato, quantidade, observacoes) {
    try {
        gerenciadorCarrinho.carregar();
        gerenciadorCarrinho.adicionar(prato, quantidade, observacoes);
        return true;
    } catch (erro) {
        alert(erro.message || "Quantidade inválida.");
        return false;
    }
}

if (campoPesquisa) {
    campoPesquisa.addEventListener("input", renderizarCardapio);
}

if (botaoLimparPesquisa && campoPesquisa) {
    botaoLimparPesquisa.addEventListener("click", () => {
        campoPesquisa.value = "";
        renderizarCardapio();
        campoPesquisa.focus();
    });
}

if (botaoFecharDetalhes) {
    botaoFecharDetalhes.onclick = () => modalDetalhes.close();
}

if (btnConfVoltar && modalConfirmacao) {
    btnConfVoltar.onclick = () => modalConfirmacao.close();
}

configurarLinksCategoria();
carregarCardapio();
