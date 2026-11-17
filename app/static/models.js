class Usuario {
    #id;
    #nome;
    #email;
    #tipo;

    constructor({ id = null, nome = "", email = "", tipo = "cliente" } = {}) {
        this.#id = id;
        this.#nome = String(nome).trim();
        this.#email = String(email).trim().toLowerCase();
        this.#tipo = String(tipo).trim().toLowerCase();
    }

    get id() {
        return this.#id;
    }

    get nome() {
        return this.#nome;
    }

    get email() {
        return this.#email;
    }

    get tipo() {
        return this.#tipo;
    }

    get ehAdministrador() {
        return this.#tipo === "administrador";
    }

    get ehCozinheiro() {
        return this.#tipo === "cozinheiro";
    }

    get ehCliente() {
        return this.#tipo === "cliente";
    }

    static validarEmail(email) {
        if (typeof email !== "string") {
            return false;
        }
        const limpo = email.trim();
        return limpo.length >= 3 && limpo.length <= 120 && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(limpo);
    }

    static validarSenha(senha) {
        if (typeof senha !== "string" || senha.length < 8) {
            return false;
        }
        return /[a-zA-ZÀ-ÿ]/.test(senha) && /\d/.test(senha);
    }
}

class Prato {
    #id;
    #nome;
    #descricao;
    #preco;
    #categoria;
    #imagem;
    #ativo;
    #tempoPreparoMin;

    constructor(dados = {}) {
        this.#id = Number(dados.id);
        this.#nome = String(dados.nome || "").trim();
        this.#descricao = String(dados.descricao || "").trim();
        this.#preco = Number(dados.preco || 0);
        this.#categoria = String(dados.categoria || "Pratos").trim();
        this.#imagem = dados.imagem || null;
        this.#ativo = Boolean(dados.ativo ?? 1);
        this.#tempoPreparoMin = Number(dados.tempo_preparo_min || 20);
    }

    get id() {
        return this.#id;
    }

    get nome() {
        return this.#nome;
    }

    get descricao() {
        return this.#descricao;
    }

    get preco() {
        return this.#preco;
    }

    get categoria() {
        return this.#categoria;
    }

    get imagem() {
        return this.#imagem;
    }

    get ativo() {
        return this.#ativo;
    }

    get tempoPreparoMin() {
        return this.#tempoPreparoMin;
    }

    get precoFormatado() {
        return Prato.formatarMoeda(this.#preco);
    }

    correspondeBusca(termo) {
        const busca = String(termo || "").trim().toLowerCase();
        if (!busca) {
            return true;
        }
        return (
            this.#nome.toLowerCase().includes(busca) ||
            this.#descricao.toLowerCase().includes(busca)
        );
    }

    static formatarMoeda(valor) {
        return Number(valor || 0).toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL"
        });
    }
}

class ItemPedido {
    #id;
    #nome;
    #preco;
    #quantidade;

    constructor(id, nome, preco, quantidade = 1) {
        this.#id = Number(id);
        this.#nome = String(nome || "").trim();
        this.#preco = Number(preco || 0);
        this.quantidade = quantidade;
    }

    get id() {
        return this.#id;
    }

    get nome() {
        return this.#nome;
    }

    get preco() {
        return this.#preco;
    }

    get quantidade() {
        return this.#quantidade;
    }

    set quantidade(valor) {
        const numero = Number(valor);
        if (!Number.isInteger(numero) || numero < 1) {
            throw new Error("A quantidade deve ser um número inteiro positivo (mínimo 1).");
        }
        this.#quantidade = numero;
    }

    get subtotal() {
        return this.#preco * this.#quantidade;
    }

    get subtotalFormatado() {
        return ItemPedido.formatarPreco(this.subtotal);
    }

    static formatarPreco(valor) {
        return Prato.formatarMoeda(valor);
    }
}

class ItemCarrinho extends ItemPedido {
    #observacoes;
    #imagem;

    constructor(dados = {}) {
        super(dados.id ?? dados.prato_id, dados.nome, dados.preco ?? dados.preco_unitario, dados.quantidade ?? 1);
        this.#observacoes = String(dados.observacoes || "").trim();
        this.#imagem = dados.imagem || null;
    }

    get observacoes() {
        return this.#observacoes;
    }

    set observacoes(texto) {
        this.#observacoes = String(texto || "").trim().slice(0, 255);
    }

    get imagem() {
        return this.#imagem;
    }

    somarQuantidade(adicional) {
        this.quantidade = this.quantidade + Number(adicional);
    }

    toJSON() {
        return {
            id: this.id,
            nome: this.nome,
            preco: this.preco,
            imagem: this.#imagem,
            quantidade: this.quantidade,
            observacoes: this.#observacoes
        };
    }

    paraPayloadPedido() {
        return {
            prato_id: this.id,
            quantidade: this.quantidade,
            observacoes: this.#observacoes
        };
    }
}

class Carrinho {
    #itens = [];
    #chaveStorage;

    constructor(identificadorUsuario = "") {
        const sufixo = identificadorUsuario ? `_${identificadorUsuario}` : "";
        this.#chaveStorage = `sabor_clic_carrinho${sufixo}`;
        this.carregar();
    }

    get itens() {
        return [...this.#itens];
    }

    get vazio() {
        return this.#itens.length === 0;
    }

    get subtotal() {
        return this.#itens.reduce((acumulador, item) => acumulador + item.subtotal, 0);
    }

    get subtotalFormatado() {
        return Prato.formatarMoeda(this.subtotal);
    }

    carregar() {
        try {
            const bruto = localStorage.getItem(this.#chaveStorage) || localStorage.getItem("sabor_clic_carrinho") || "[]";
            const lista = JSON.parse(bruto);
            if (!Array.isArray(lista)) {
                this.#itens = [];
                return;
            }
            this.#itens = lista
                .filter(item => item && Number.isInteger(Number(item.quantidade)) && Number(item.quantidade) >= 1)
                .map(item => new ItemCarrinho(item));
        } catch (_erro) {
            this.#itens = [];
        }
    }

    salvar() {
        const serializado = JSON.stringify(this.#itens.map(item => item.toJSON()));
        localStorage.setItem(this.#chaveStorage, serializado);
        localStorage.setItem("sabor_clic_carrinho", serializado);
    }

    adicionar(prato, quantidade = 1, observacoes = "") {
        const obsLimpa = String(observacoes || "").trim().slice(0, 255);
        const novoItem = new ItemCarrinho({
            id: prato.id,
            nome: prato.nome,
            preco: prato.preco,
            imagem: prato.imagem,
            quantidade,
            observacoes: obsLimpa
        });

        const existente = this.#itens.find(
            item => item.id === novoItem.id && item.observacoes === novoItem.observacoes
        );

        if (existente) {
            existente.somarQuantidade(novoItem.quantidade);
        } else {
            this.#itens.push(novoItem);
        }

        this.salvar();
        return novoItem;
    }

    alterarQuantidade(indice, diferenca) {
        const item = this.#itens[indice];
        if (!item) {
            return;
        }
        const novaQuantidade = item.quantidade + Number(diferenca);
        if (novaQuantidade <= 0) {
            this.remover(indice);
            return;
        }
        item.quantidade = novaQuantidade;
        this.salvar();
    }

    atualizarObservacoes(indice, observacoes) {
        const item = this.#itens[indice];
        if (!item) {
            return;
        }
        item.observacoes = observacoes;
        this.salvar();
    }

    remover(indice) {
        this.#itens = this.#itens.filter((_item, idx) => idx !== indice);
        this.salvar();
    }

    limpar() {
        this.#itens = [];
        localStorage.removeItem(this.#chaveStorage);
        localStorage.removeItem("sabor_clic_carrinho");
    }

    paraPayload() {
        return {
            itens: this.#itens.map(item => item.paraPayloadPedido())
        };
    }
}

class Pedido {
    #id;
    #clienteNome;
    #status;
    #dataPedido;
    #total;
    #tempoEstimado;
    #observacoes;
    #itens;

    constructor(dados = {}) {
        this.#id = Number(dados.id);
        this.#clienteNome = String(dados.cliente_nome || "Cliente").trim();
        this.#status = String(dados.status || "Aguardando").trim();
        this.#dataPedido = dados.data_pedido || "";
        this.#total = Number(dados.total || 0);
        this.#tempoEstimado = dados.tempo_estimado ? Number(dados.tempo_estimado) : null;
        this.#observacoes = String(dados.observacoes || "").trim();
        this.#itens = Array.isArray(dados.itens) ? dados.itens : [];
    }

    get id() {
        return this.#id;
    }

    get clienteNome() {
        return this.#clienteNome;
    }

    get status() {
        return this.#status;
    }

    get dataPedido() {
        return this.#dataPedido;
    }

    get total() {
        return this.#total;
    }

    get totalFormatado() {
        return Prato.formatarMoeda(this.#total);
    }

    get tempoEstimado() {
        return this.#tempoEstimado;
    }

    get observacoes() {
        return this.#observacoes;
    }

    get itens() {
        return [...this.#itens];
    }

    get proximoStatus() {
        if (this.#status === "Aguardando") {
            return "Iniciando Preparo";
        }
        if (this.#status === "Iniciando Preparo") {
            return "Pronto para Entrega";
        }
        if (this.#status === "Pronto para Entrega") {
            return "Entregue";
        }
        return null;
    }

    get minutosDecorridos() {
        if (!this.#dataPedido) {
            return 0;
        }
        const iso = this.#dataPedido.includes("T")
            ? this.#dataPedido
            : `${this.#dataPedido.replace(" ", "T")}Z`;
        const data = new Date(iso);
        if (Number.isNaN(data.getTime())) {
            return 0;
        }
        const diff = Math.max(0, Math.floor((Date.now() - data.getTime()) / 60000));
        return diff;
    }
}

class Bancada {
    #id;
    #codigo;
    #descricao;
    #valorHora;
    #valorCaucao;
    #statusOperacional;

    constructor(dados = {}) {
        this.#id = Number(dados.id ?? dados.id_bancada);
        this.#codigo = String(dados.cod_identificacao || "").trim();
        this.#descricao = String(dados.descricao || "").trim();
        this.#valorHora = Number(dados.valor_hora || 0);
        this.#valorCaucao = Number(dados.valor_caucao || 0);
        this.#statusOperacional = String(dados.status_operacional || "DISPONIVEL").trim();
    }

    get id() {
        return this.#id;
    }

    get codigo() {
        return this.#codigo;
    }

    get descricao() {
        return this.#descricao;
    }

    get valorHora() {
        return this.#valorHora;
    }

    get valorCaucao() {
        return this.#valorCaucao;
    }

    get statusOperacional() {
        return this.#statusOperacional;
    }

    get valorHoraFormatado() {
        return Prato.formatarMoeda(this.#valorHora);
    }

    get valorCaucaoFormatado() {
        return Prato.formatarMoeda(this.#valorCaucao);
    }
}

class Icones {
    static criar(nome, classeExtra = "") {
        const ns = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(ns, "svg");
        svg.setAttribute("class", classeExtra ? `icone-svg ${classeExtra}` : "icone-svg");
        svg.setAttribute("aria-hidden", "true");
        const uso = document.createElementNS(ns, "use");
        uso.setAttribute("href", `#ico-${nome}`);
        svg.appendChild(uso);
        return svg;
    }

    static preencher(elemento, nomeIcone, texto, classeExtra = "") {
        const span = document.createElement("span");
        span.textContent = texto;
        elemento.replaceChildren(Icones.criar(nomeIcone, classeExtra), span);
        return elemento;
    }
}

window.Icones = Icones;
window.Usuario = Usuario;
window.Prato = Prato;
window.Produto = Prato;
window.ItemPedido = ItemPedido;
window.ItemCarrinho = ItemCarrinho;
window.Carrinho = Carrinho;
window.Pedido = Pedido;
window.Bancada = Bancada;
