const mensagemAdmin = document.getElementById("mensagem-admin");
const mensagemFuncionario = document.getElementById("mensagem-funcionario");
const listaProdutosAdmin = document.getElementById("produtos-admin");
const listaFuncionariosAdmin = document.getElementById("funcionarios-admin");
const listaClientesAdmin = document.getElementById("clientes-admin");
const listaBancadasAdmin = document.getElementById("bancadas-admin");
const listaReservasBancadasAdmin = document.getElementById("reservas-bancadas-admin");
const listaPedidosAdmin = document.getElementById("pedidos-admin");
const historicoStatusAdmin = document.getElementById("historico-status-admin");

const kpiPedidos = document.getElementById("kpi-pedidos");
const kpiFaturamentoDelivery = document.getElementById("kpi-faturamento-delivery");
const kpiTicketMedio = document.getElementById("kpi-ticket-medio");
const kpiReceitaBancadas = document.getElementById("kpi-receita-bancadas");
const kpiFaturamentoGlobal = document.getElementById("kpi-faturamento-global");
const kpiAlertasEstoque = document.getElementById("kpi-alertas-estoque");

const rankingPratosAdmin = document.getElementById("ranking-pratos-admin");
const produtividadeBancadasAdmin = document.getElementById("produtividade-bancadas-admin");
const listaAlertasEstoqueAdmin = document.getElementById("lista-alertas-estoque-admin");
const statusPedidosAdmin = document.getElementById("status-pedidos-admin");

const buscaPratoAdmin = document.getElementById("busca-prato-admin");
const filtroCategoriaAdmin = document.getElementById("filtro-categoria-admin");
const filtroStatusAdmin = document.getElementById("filtro-status-admin");

const filtroReservaBancada = document.getElementById("filtro-reserva-bancada");
const filtroReservaData = document.getElementById("filtro-reserva-data");
const filtroReservaStatus = document.getElementById("filtro-reserva-status");
const filtroPedidoStatusAdmin = document.getElementById("filtro-pedido-status-admin");

const modalEditarPrato = document.getElementById("modal-editar-prato");
const formEditarPrato = document.getElementById("form-editar-prato");
const botaoFecharModalPrato = document.getElementById("fechar-modal-prato");

const modalEditarBancada = document.getElementById("modal-editar-bancada");
const formEditarBancada = document.getElementById("form-editar-bancada");
const botaoFecharModalBancada = document.getElementById("fechar-modal-bancada");

const modalEditarReserva = document.getElementById("modal-editar-reserva");
const formEditarReserva = document.getElementById("form-editar-reserva");
const botaoFecharModalReserva = document.getElementById("fechar-modal-reserva");
const avisoConflitoModalAdmin = document.getElementById("aviso-conflito-modal-admin");

const modalEditarPedido = document.getElementById("modal-editar-pedido");
const formEditarPedido = document.getElementById("form-editar-pedido");
const botaoFecharModalPedido = document.getElementById("fechar-modal-pedido");

const modalEditarFuncionario = document.getElementById("modal-editar-funcionario");
const formEditarFuncionario = document.getElementById("form-editar-funcionario");
const botaoFecharModalFuncionario = document.getElementById("fechar-modal-funcionario");

const modalEditarCliente = document.getElementById("modal-editar-cliente");
const formEditarCliente = document.getElementById("form-editar-cliente");
const botaoFecharModalCliente = document.getElementById("fechar-modal-cliente");

let cachePratosAdmin = [];
let cacheBancadasAdmin = [];
let cacheReservasAdmin = [];
let cachePedidosAdmin = [];

function mostrarAvisoAdmin(texto, ehErro = false) {
    if (mensagemAdmin) {
        mensagemAdmin.textContent = texto;
        mensagemAdmin.className = ehErro ? "aviso erro" : "aviso";
    }
}

function paraInputDateTimeLocal(dataSql) {
    if (!dataSql) {
        return "";
    }
    return String(dataSql).replace(" ", "T").slice(0, 16);
}

function normalizarDataHoraComparacao(valor) {
    if (!valor) {
        return "";
    }
    const base = String(valor).trim().replace("T", " ");
    return base.length === 16 ? `${base}:00` : base.slice(0, 19);
}

function configurarAbas() {
    const botoesAbas = document.querySelectorAll(".aba-btn");
    const conteudosAbas = document.querySelectorAll(".aba-conteudo");

    botoesAbas.forEach(botao => {
        botao.addEventListener("click", () => {
            const alvo = botao.dataset.aba;
            botoesAbas.forEach(b => b.classList.toggle("ativa", b === botao));
            conteudosAbas.forEach(secao => secao.classList.toggle("ativa", secao.id === alvo));
        });
    });
}

function renderizarKpisERelatorios(resumo) {
    if (kpiPedidos) {
        kpiPedidos.textContent = String(resumo.pedidos ?? 0);
    }
    if (kpiFaturamentoDelivery) {
        kpiFaturamentoDelivery.textContent = Prato.formatarMoeda(resumo.faturamento || 0);
    }
    if (kpiTicketMedio) {
        kpiTicketMedio.textContent = Prato.formatarMoeda(resumo.ticket_medio || 0);
    }
    if (kpiReceitaBancadas) {
        kpiReceitaBancadas.textContent = Prato.formatarMoeda(resumo.receita_bancadas || 0);
    }
    if (kpiFaturamentoGlobal) {
        kpiFaturamentoGlobal.textContent = Prato.formatarMoeda(resumo.faturamento_global || 0);
    }
    const alertas = resumo.alertas_estoque || [];
    if (kpiAlertasEstoque) {
        kpiAlertasEstoque.textContent = String(alertas.length);
    }

    if (rankingPratosAdmin) {
        rankingPratosAdmin.replaceChildren();
        const ranking = resumo.ranking_pratos || [];
        if (!ranking.length) {
            rankingPratosAdmin.textContent = "Nenhum prato cadastrado.";
        } else {
            ranking.forEach((item, idx) => {
                const linha = document.createElement("article");
                linha.className = "produto-admin";
                const texto = document.createElement("strong");
                texto.textContent = `${idx + 1}º ${item.nome} (${item.categoria}) — ${item.unidades_vendidas} un. vendidas | Receita: ${Prato.formatarMoeda(item.receita_prato)}`;
                linha.append(texto);
                rankingPratosAdmin.append(linha);
            });
        }
    }

    if (produtividadeBancadasAdmin) {
        produtividadeBancadasAdmin.replaceChildren();
        const prod = resumo.produtividade_bancadas || [];
        if (!prod.length) {
            produtividadeBancadasAdmin.textContent = "Nenhuma bancada cadastrada.";
        } else {
            prod.forEach(b => {
                const linha = document.createElement("article");
                linha.className = "produto-admin";
                const texto = document.createElement("strong");
                texto.textContent = `${b.cod_identificacao} (${b.status_operacional}) — ${b.total_locacoes} locações | ${b.total_horas_utilizadas}h | Receita: ${Prato.formatarMoeda(b.receita_total_gerada)}`;
                linha.append(texto);
                produtividadeBancadasAdmin.append(linha);
            });
        }
    }

    if (listaAlertasEstoqueAdmin) {
        listaAlertasEstoqueAdmin.replaceChildren();
        if (!alertas.length) {
            listaAlertasEstoqueAdmin.textContent = "Todos os pratos possuem estoque regular (> 10 unidades).";
        } else {
            alertas.forEach(item => {
                const linha = document.createElement("article");
                linha.className = "produto-admin";
                const texto = document.createElement("strong");
                texto.textContent = `${item.nome} (${item.categoria}) — Saldo: ${item.estoque} un.`;
                const badge = document.createElement("span");
                badge.className = "badge-alerta";
                badge.textContent = item.status_estoque;
                linha.append(texto, badge);
                listaAlertasEstoqueAdmin.append(linha);
            });
        }
    }

    if (statusPedidosAdmin) {
        statusPedidosAdmin.replaceChildren();
        const porStatus = resumo.por_status || [];
        if (!porStatus.length) {
            statusPedidosAdmin.textContent = "Nenhum pedido registrado até o momento.";
        } else {
            porStatus.forEach(item => {
                const linha = document.createElement("article");
                linha.className = "produto-admin";
                const texto = document.createElement("strong");
                texto.textContent = `${item.status}: ${item.quantidade} pedido(s)`;
                linha.append(texto);
                statusPedidosAdmin.append(linha);
            });
        }
    }
}

function renderizarListaProdutosAdmin() {
    if (!listaProdutosAdmin) {
        return;
    }

    const termo = (buscaPratoAdmin ? buscaPratoAdmin.value : "").trim().toLowerCase();
    const catFiltro = filtroCategoriaAdmin ? filtroCategoriaAdmin.value : "";
    const statusFiltro = filtroStatusAdmin ? filtroStatusAdmin.value : "";

    const filtrados = cachePratosAdmin.filter(item => {
        const prato = new Prato(item);
        if (termo && !prato.correspondeBusca(termo)) {
            return false;
        }
        if (catFiltro && prato.categoria !== catFiltro) {
            return false;
        }
        const qtdEstoque = Number(item.estoque ?? 50);
        if (statusFiltro === "ativos" && !prato.ativo) {
            return false;
        }
        if (statusFiltro === "inativos" && prato.ativo) {
            return false;
        }
        if (statusFiltro === "estoque_baixo" && qtdEstoque > 10) {
            return false;
        }
        return true;
    });

    listaProdutosAdmin.replaceChildren();

    if (filtrados.length === 0) {
        listaProdutosAdmin.textContent = "Nenhum prato encontrado com os filtros selecionados.";
        return;
    }

    filtrados.forEach(item => {
        const prato = new Prato(item);
        const qtdEstoque = Number(item.estoque ?? 50);

        const card = document.createElement("article");
        card.className = "produto-admin card-prato-admin";

        const miniatura = document.createElement("div");
        miniatura.className = "miniatura-admin";
        if (prato.imagem) {
            const img = document.createElement("img");
            img.src = `/static/${prato.imagem}`;
            img.alt = prato.nome;
            miniatura.append(img);
        } else {
            miniatura.append(Icones.criar("utensils", "icone-svg-lg"));
        }

        const blocoInfo = document.createElement("div");
        blocoInfo.className = "info-prato-admin";

        const titulo = document.createElement("strong");
        titulo.textContent = `${prato.nome} — ${prato.precoFormatado}`;

        const meta = document.createElement("small");
        const statusTexto = prato.ativo ? "Ativo" : "Inativo";
        meta.textContent = `Categoria: ${prato.categoria} · Preparo: ${prato.tempoPreparoMin} min · Status: ${statusTexto}`;

        const descricao = document.createElement("p");
        descricao.textContent = prato.descricao;

        blocoInfo.append(titulo, meta, descricao);

        const blocoEstoque = document.createElement("div");
        blocoEstoque.className = "controle-estoque-admin";

        const badgeEstoque = document.createElement("span");
        badgeEstoque.className = qtdEstoque <= 10 ? "badge-alerta" : "badge-normal";
        badgeEstoque.textContent = `Estoque: ${qtdEstoque} un.`;

        const btnMenosEstoque = document.createElement("button");
        btnMenosEstoque.type = "button";
        btnMenosEstoque.textContent = "-1";
        btnMenosEstoque.disabled = qtdEstoque <= 0;
        btnMenosEstoque.onclick = () => alterarEstoqueRapido(prato.id, Math.max(0, qtdEstoque - 1));

        const btnMaisEstoque = document.createElement("button");
        btnMaisEstoque.type = "button";
        btnMaisEstoque.textContent = "+10";
        btnMaisEstoque.onclick = () => alterarEstoqueRapido(prato.id, qtdEstoque + 10);

        blocoEstoque.append(badgeEstoque, btnMenosEstoque, btnMaisEstoque);

        const blocoAcoes = document.createElement("div");
        blocoAcoes.className = "acoes-item-admin";

        const botaoEditar = document.createElement("button");
        botaoEditar.type = "button";
        botaoEditar.className = "botao";
        botaoEditar.textContent = "Editar";
        botaoEditar.onclick = () => abrirModalEditarPrato(item);

        const botaoStatus = document.createElement("button");
        botaoStatus.type = "button";
        botaoStatus.className = "botao-secundario";
        botaoStatus.textContent = prato.ativo ? "Desativar" : "Reativar";
        botaoStatus.onclick = () => alternarStatusProduto(item);

        blocoAcoes.append(botaoEditar, botaoStatus);

        card.append(miniatura, blocoInfo, blocoEstoque, blocoAcoes);
        listaProdutosAdmin.append(card);
    });
}

function renderizarBancadasAdmin() {
    if (!listaBancadasAdmin) {
        return;
    }

    if (filtroReservaBancada) {
        const valorAtual = filtroReservaBancada.value;
        filtroReservaBancada.replaceChildren();
        const optTodas = document.createElement("option");
        optTodas.value = "";
        optTodas.textContent = "Todas as bancadas";
        filtroReservaBancada.append(optTodas);
        cacheBancadasAdmin.forEach(b => {
            const opt = document.createElement("option");
            opt.value = String(b.id);
            opt.textContent = `${b.cod_identificacao} (${b.status_operacional})`;
            filtroReservaBancada.append(opt);
        });
        filtroReservaBancada.value = valorAtual;
    }

    const selectModalReserva = document.getElementById("edit-reserva-bancada");
    if (selectModalReserva) {
        selectModalReserva.replaceChildren();
        cacheBancadasAdmin.forEach(b => {
            const opt = document.createElement("option");
            opt.value = String(b.id);
            opt.textContent = `${b.cod_identificacao} — ${Prato.formatarMoeda(b.valor_hora)}/h (Caução: ${Prato.formatarMoeda(b.valor_caucao)})`;
            selectModalReserva.append(opt);
        });
    }

    listaBancadasAdmin.replaceChildren();

    cacheBancadasAdmin.forEach(dadosBancada => {
        const bancada = new Bancada(dadosBancada);
        const reservasAtivas = cacheReservasAdmin.filter(
            r => Number(r.bancada_id) === bancada.id && ["SOLICITADA", "CONFIRMADA"].includes(r.status_reserva)
        );

        const card = document.createElement("article");
        card.className = "produto-admin";

        const info = document.createElement("div");
        info.className = "info-prato-admin";
        info.style.flex = "1";

        const titulo = document.createElement("strong");
        titulo.textContent = `${bancada.codigo} — Hora: ${bancada.valorHoraFormatado} | Caução: ${bancada.valorCaucaoFormatado}`;

        const meta = document.createElement("small");
        meta.textContent = `Status: ${bancada.statusOperacional} · Reservas ativas na agenda: ${reservasAtivas.length}`;

        const desc = document.createElement("p");
        desc.textContent = `Equipamentos: ${bancada.descricao}`;

        info.append(titulo, meta, desc);

        const badge = document.createElement("span");
        badge.className = bancada.statusOperacional === "DISPONIVEL" ? "badge-normal" : "badge-alerta";
        badge.textContent = bancada.statusOperacional;

        const botaoEditar = document.createElement("button");
        botaoEditar.type = "button";
        botaoEditar.className = "botao";
        botaoEditar.textContent = "Editar bancada";
        botaoEditar.onclick = () => abrirModalEditarBancada(dadosBancada);

        card.append(info, badge, botaoEditar);
        listaBancadasAdmin.append(card);
    });
}

function renderizarAgendaReservasAdmin() {
    if (!listaReservasBancadasAdmin) {
        return;
    }

    const bancadaFiltro = filtroReservaBancada ? filtroReservaBancada.value : "";
    const dataFiltro = filtroReservaData ? filtroReservaData.value : "";
    const statusFiltro = filtroReservaStatus ? filtroReservaStatus.value : "";

    const filtradas = cacheReservasAdmin.filter(r => {
        if (bancadaFiltro && String(r.bancada_id) !== String(bancadaFiltro)) {
            return false;
        }
        if (statusFiltro && r.status_reserva !== statusFiltro) {
            return false;
        }
        if (dataFiltro) {
            const iniData = String(r.data_hora_inicio || "").slice(0, 10);
            const fimData = String(r.data_hora_fim || "").slice(0, 10);
            if (iniData > dataFiltro || fimData < dataFiltro) {
                return false;
            }
        }
        return true;
    });

    listaReservasBancadasAdmin.replaceChildren();

    if (filtradas.length === 0) {
        listaReservasBancadasAdmin.textContent = "Nenhuma reserva encontrada para os filtros selecionados.";
        return;
    }

    filtradas.forEach(r => {
        const card = document.createElement("article");
        card.className = "produto-admin";

        const info = document.createElement("div");
        info.className = "info-prato-admin";
        info.style.flex = "1";

        const titulo = document.createElement("strong");
        const duracao = r.duracao_horas ? ` (${r.duracao_horas}h)` : "";
        titulo.textContent = `Reserva #${r.id_reserva} · ${r.cod_identificacao} | ${r.data_hora_inicio} até ${r.data_hora_fim}${duracao}`;

        const metaCliente = document.createElement("small");
        const contato = r.cliente_email ? ` (${r.cliente_email}${r.cliente_telefone ? " · " + r.cliente_telefone : ""})` : "";
        metaCliente.textContent = `Locatário: ${r.cliente_nome || "Cliente #" + r.cliente_id}${contato} · Equipamentos: ${r.bancada_descricao || "-"}`;

        const valores = document.createElement("p");
        const totalGeral = Number(r.valor_total_horas || 0) + Number(r.valor_adicionais || 0);
        valores.textContent = `Locação: ${Prato.formatarMoeda(r.valor_total_horas)} | Caução: ${Prato.formatarMoeda(r.valor_caucao_pago)} | Adicionais: ${Prato.formatarMoeda(r.valor_adicionais)} | Total c/ adicionais: ${Prato.formatarMoeda(totalGeral)}`;

        info.append(titulo, metaCliente, valores);

        const badge = document.createElement("span");
        badge.className = r.status_reserva === "CANCELADA" ? "badge-alerta" : "badge-normal";
        badge.textContent = r.status_reserva;

        const botaoEditar = document.createElement("button");
        botaoEditar.type = "button";
        botaoEditar.className = "botao";
        botaoEditar.textContent = "Editar reserva";
        botaoEditar.onclick = () => abrirModalEditarReserva(r);

        card.append(info, badge, botaoEditar);
        listaReservasBancadasAdmin.append(card);
    });
}

function renderizarPedidosEAuditoriaAdmin(historicoStatus = null) {
    if (listaPedidosAdmin) {
        const statusFiltro = filtroPedidoStatusAdmin ? filtroPedidoStatusAdmin.value : "";
        const filtrados = cachePedidosAdmin.filter(p => !statusFiltro || p.status === statusFiltro);

        listaPedidosAdmin.replaceChildren();
        if (!filtrados.length) {
            listaPedidosAdmin.textContent = "Nenhum pedido encontrado.";
        } else {
            filtrados.forEach(p => {
                const pedido = new Pedido(p);
                const card = document.createElement("article");
                card.className = "produto-admin";

                const info = document.createElement("div");
                info.className = "info-prato-admin";
                info.style.flex = "1";

                const titulo = document.createElement("strong");
                titulo.textContent = `Pedido #${pedido.id} · ${pedido.clienteNome} — Total: ${pedido.totalFormatado}`;

                const itensStr = pedido.itens
                    .map(i => `${i.quantidade}× ${i.nome}${i.observacoes ? " [" + i.observacoes + "]" : ""}`)
                    .join(", ");
                const pItens = document.createElement("p");
                pItens.textContent = `Itens: ${itensStr}`;

                const meta = document.createElement("small");
                const obsTxt = pedido.observacoes ? ` · Obs: ${pedido.observacoes}` : "";
                meta.textContent = `Data: ${pedido.dataPedido} · Preparo estimado: ${pedido.tempoEstimado || 20} min${obsTxt}`;

                info.append(titulo, pItens, meta);

                const badge = document.createElement("span");
                badge.className = pedido.status === "Cancelado" ? "badge-alerta" : "badge-normal";
                badge.textContent = pedido.status;

                const botaoEditar = document.createElement("button");
                botaoEditar.type = "button";
                botaoEditar.className = "botao";
                botaoEditar.textContent = "Editar pedido";
                botaoEditar.onclick = () => abrirModalEditarPedido(p);

                card.append(info, badge, botaoEditar);
                listaPedidosAdmin.append(card);
            });
        }
    }

    if (historicoStatusAdmin && Array.isArray(historicoStatus)) {
        historicoStatusAdmin.replaceChildren();
        if (!historicoStatus.length) {
            historicoStatusAdmin.textContent = "Nenhuma mudança de status registrada pela trigger ainda.";
        } else {
            historicoStatus.forEach(h => {
                const card = document.createElement("article");
                card.className = "produto-admin";
                const texto = document.createElement("small");
                texto.textContent = `[${h.alterado_em}] Pedido #${h.pedido_id} (${h.cliente_nome}) alterado para "${h.status}"`;
                card.append(texto);
                historicoStatusAdmin.append(card);
            });
        }
    }
}

function renderizarEquipeEClientesAdmin(funcionariosBrutos = [], clientesBrutos = []) {
    if (listaFuncionariosAdmin) {
        listaFuncionariosAdmin.replaceChildren();
        if (!funcionariosBrutos.length) {
            listaFuncionariosAdmin.textContent = "Nenhum funcionário cadastrado.";
        } else {
            funcionariosBrutos.forEach(f => {
                const funcionario = new Usuario(f);
                const card = document.createElement("article");
                card.className = "produto-admin";

                const info = document.createElement("div");
                info.className = "info-prato-admin";
                info.style.flex = "1";

                const titulo = document.createElement("strong");
                titulo.textContent = `${funcionario.nome} (${funcionario.tipo})`;

                const sub = document.createElement("small");
                sub.textContent = `E-mail: ${funcionario.email}${f.telefone ? " · Tel: " + f.telefone : ""}`;

                info.append(titulo, sub);

                const botaoEditar = document.createElement("button");
                botaoEditar.type = "button";
                botaoEditar.className = "botao";
                botaoEditar.textContent = "Editar";
                botaoEditar.onclick = () => abrirModalEditarFuncionario(f);

                const botaoRemover = document.createElement("button");
                botaoRemover.type = "button";
                botaoRemover.className = "botao-secundario";
                botaoRemover.textContent = "Remover";
                botaoRemover.onclick = () => removerFuncionarioAdmin(f);

                card.append(info, botaoEditar, botaoRemover);
                listaFuncionariosAdmin.append(card);
            });
        }
    }

    if (listaClientesAdmin) {
        listaClientesAdmin.replaceChildren();
        if (!clientesBrutos.length) {
            listaClientesAdmin.textContent = "Nenhum cliente cadastrado.";
        } else {
            clientesBrutos.forEach(cli => {
                const card = document.createElement("article");
                card.className = "produto-admin";

                const info = document.createElement("div");
                info.className = "info-prato-admin";
                info.style.flex = "1";

                const titulo = document.createElement("strong");
                titulo.textContent = `#${cli.id} · ${cli.nome} — ${cli.email}`;

                const endStr = cli.rua
                    ? `${cli.rua}, ${cli.numero} - ${cli.bairro}, ${cli.cidade}/${cli.estado} (CEP: ${cli.cep})`
                    : "Endereço não informado";
                const sub = document.createElement("small");
                sub.textContent = `Tel: ${cli.telefone || "-"} · CPF: ${cli.cpf || "-"} · Endereço: ${endStr}`;

                info.append(titulo, sub);

                const botaoEditar = document.createElement("button");
                botaoEditar.type = "button";
                botaoEditar.className = "botao";
                botaoEditar.textContent = "Editar cliente";
                botaoEditar.onclick = () => abrirModalEditarCliente(cli);

                card.append(info, botaoEditar);
                listaClientesAdmin.append(card);
            });
        }
    }
}

function abrirModalEditarPedido(pedido) {
    if (!modalEditarPedido) {
        return;
    }
    document.getElementById("edit-pedido-id").value = pedido.id;
    document.getElementById("edit-pedido-resumo").textContent = `Pedido #${pedido.id} — Cliente: ${pedido.cliente_nome || "Cliente"}`;
    document.getElementById("edit-pedido-status").value = pedido.status || "Aguardando";
    document.getElementById("edit-pedido-tempo").value = pedido.tempo_estimado || 20;
    document.getElementById("edit-pedido-observacoes").value = pedido.observacoes || "";
    modalEditarPedido.showModal();
}

function abrirModalEditarFuncionario(funcionario) {
    if (!modalEditarFuncionario) {
        return;
    }
    document.getElementById("edit-func-id").value = funcionario.id;
    document.getElementById("edit-func-nome").value = funcionario.nome || "";
    document.getElementById("edit-func-email").value = funcionario.email || "";
    document.getElementById("edit-func-telefone").value = funcionario.telefone || "";
    document.getElementById("edit-func-tipo").value = funcionario.tipo || "cozinheiro";
    document.getElementById("edit-func-senha").value = "";
    modalEditarFuncionario.showModal();
}

async function removerFuncionarioAdmin(funcionario) {
    try {
        const resposta = await fetch(`/api/admin/funcionarios/${funcionario.id}`, {
            method: "DELETE"
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao remover funcionário.");
        }
        mostrarAvisoAdmin(dados.mensagem);
        await atualizarAdmin();
    } catch (erro) {
        mostrarAvisoAdmin(erro.message, true);
    }
}

function abrirModalEditarCliente(cliente) {
    if (!modalEditarCliente) {
        return;
    }
    document.getElementById("edit-cli-id").value = cliente.id;
    document.getElementById("edit-cli-nome").value = cliente.nome || "";
    document.getElementById("edit-cli-email").value = cliente.email || "";
    document.getElementById("edit-cli-telefone").value = cliente.telefone || "";
    document.getElementById("edit-cli-cpf").value = cliente.cpf || "";
    document.getElementById("edit-cli-rua").value = cliente.rua || "";
    document.getElementById("edit-cli-numero").value = cliente.numero || "";
    document.getElementById("edit-cli-bairro").value = cliente.bairro || "";
    document.getElementById("edit-cli-cidade").value = cliente.cidade || "";
    document.getElementById("edit-cli-estado").value = cliente.estado || "SP";
    document.getElementById("edit-cli-cep").value = cliente.cep || "";
    modalEditarCliente.showModal();
}

function abrirModalEditarBancada(bancada) {
    if (!modalEditarBancada) {
        return;
    }
    document.getElementById("edit-bancada-id").value = bancada.id;
    document.getElementById("edit-bancada-codigo").value = bancada.cod_identificacao || "";
    document.getElementById("edit-bancada-descricao").value = bancada.descricao || "";
    document.getElementById("edit-bancada-hora").value = Number(bancada.valor_hora || 0).toFixed(2);
    document.getElementById("edit-bancada-caucao").value = Number(bancada.valor_caucao || 0).toFixed(2);
    document.getElementById("edit-bancada-status").value = bancada.status_operacional || "DISPONIVEL";
    modalEditarBancada.showModal();
}

function verificarColisaoNoModalAdmin() {
    if (!avisoConflitoModalAdmin) {
        return;
    }
    const idAtual = Number(document.getElementById("edit-reserva-id").value);
    const idBancada = Number(document.getElementById("edit-reserva-bancada").value);
    const inicio = normalizarDataHoraComparacao(document.getElementById("edit-reserva-inicio").value);
    const fim = normalizarDataHoraComparacao(document.getElementById("edit-reserva-fim").value);
    const status = document.getElementById("edit-reserva-status").value;

    if (!inicio || !fim || status === "CANCELADA") {
        avisoConflitoModalAdmin.textContent = "";
        return;
    }

    if (fim <= inicio) {
        avisoConflitoModalAdmin.className = "aviso erro icone-inline";
        Icones.preencher(
            avisoConflitoModalAdmin,
            "alert",
            "O horário final deve ser posterior ao horário inicial."
        );
        return;
    }

    const conflito = cacheReservasAdmin.find(r =>
        Number(r.id_reserva) !== idAtual &&
        Number(r.bancada_id) === idBancada &&
        ["SOLICITADA", "CONFIRMADA"].includes(r.status_reserva) &&
        String(r.data_hora_inicio) < fim &&
        String(r.data_hora_fim) > inicio
    );

    if (conflito) {
        avisoConflitoModalAdmin.className = "aviso erro icone-inline";
        Icones.preencher(
            avisoConflitoModalAdmin,
            "alert",
            `Colisão detectada: choca com a Reserva #${conflito.id_reserva} (${conflito.data_hora_inicio} até ${conflito.data_hora_fim}).`
        );
    } else {
        avisoConflitoModalAdmin.className = "aviso icone-inline";
        Icones.preencher(
            avisoConflitoModalAdmin,
            "check",
            "Horário livre nesta bancada (sem colisão)."
        );
    }
}

function abrirModalEditarReserva(reserva) {
    if (!modalEditarReserva) {
        return;
    }
    document.getElementById("edit-reserva-id").value = reserva.id_reserva;
    document.getElementById("edit-reserva-cliente-info").textContent = `Reserva #${reserva.id_reserva} — Locatário: ${reserva.cliente_nome || "Cliente #" + reserva.cliente_id}`;
    document.getElementById("edit-reserva-bancada").value = String(reserva.bancada_id);
    document.getElementById("edit-reserva-inicio").value = paraInputDateTimeLocal(reserva.data_hora_inicio);
    document.getElementById("edit-reserva-fim").value = paraInputDateTimeLocal(reserva.data_hora_fim);
    document.getElementById("edit-reserva-status").value = reserva.status_reserva || "CONFIRMADA";
    document.getElementById("edit-reserva-adicionais").value = Number(reserva.valor_adicionais || 0).toFixed(2);
    verificarColisaoNoModalAdmin();
    modalEditarReserva.showModal();
}

async function alterarEstoqueRapido(idPrato, novaQuantidade) {
    try {
        const resposta = await fetch(`/api/admin/pratos/${idPrato}/estoque`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estoque: novaQuantidade })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao ajustar estoque.");
        }
        mostrarAvisoAdmin(dados.mensagem);
        await atualizarAdmin();
    } catch (erro) {
        mostrarAvisoAdmin(erro.message, true);
    }
}

function abrirModalEditarPrato(prato) {
    if (!modalEditarPrato) {
        return;
    }
    document.getElementById("edit-prato-id").value = prato.id;
    document.getElementById("edit-prato-nome").value = prato.nome || "";
    document.getElementById("edit-prato-descricao").value = prato.descricao || "";
    document.getElementById("edit-prato-categoria").value = prato.categoria || "Pratos";
    document.getElementById("edit-prato-ativo").value = prato.ativo ? "1" : "0";
    document.getElementById("edit-prato-preco").value = Number(prato.preco || 0).toFixed(2);
    document.getElementById("edit-prato-tempo").value = prato.tempo_preparo_min || 20;
    document.getElementById("edit-prato-estoque").value = prato.estoque ?? 50;
    document.getElementById("edit-prato-imagem").value = "";
    document.getElementById("edit-prato-remover-imagem").checked = false;

    const previewBox = document.getElementById("edit-prato-preview-box");
    previewBox.replaceChildren();
    if (prato.imagem) {
        const img = document.createElement("img");
        img.src = `/static/${prato.imagem}`;
        img.alt = prato.nome;
        const legenda = document.createElement("small");
        legenda.textContent = "Foto atual cadastrada";
        previewBox.append(img, legenda);
    } else {
        const semFoto = document.createElement("small");
        semFoto.textContent = "Prato sem foto personalizada cadastrada.";
        previewBox.append(semFoto);
    }

    modalEditarPrato.showModal();
}

async function atualizarAdmin() {
    try {
        const [r1, r2, r3] = await Promise.all([
            fetch("/api/admin/pratos"),
            fetch("/api/admin/relatorio"),
            fetch("/api/pedidos")
        ]);

        if (!r1.ok || !r2.ok) {
            throw new Error("Erro ao carregar dados do painel administrativo.");
        }

        cachePratosAdmin = await r1.json();
        const resumo = await r2.json();
        cachePedidosAdmin = r3.ok ? await r3.json() : [];

        cacheBancadasAdmin = resumo.bancadas || [];
        cacheReservasAdmin = resumo.reservas_bancadas || [];

        renderizarKpisERelatorios(resumo);
        renderizarListaProdutosAdmin();
        renderizarBancadasAdmin();
        renderizarAgendaReservasAdmin();
        renderizarPedidosEAuditoriaAdmin(resumo.historico_status || []);
        renderizarEquipeEClientesAdmin(resumo.funcionarios || [], resumo.clientes || []);
    } catch (erro) {
        mostrarAvisoAdmin(erro.message, true);
    }
}

async function alternarStatusProduto(prato) {
    try {
        if (prato.ativo) {
            const resposta = await fetch(`/api/admin/pratos/${prato.id}`, {
                method: "DELETE"
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao desativar produto.");
            }
            mostrarAvisoAdmin(dados.mensagem);
        } else {
            const resposta = await fetch(`/api/admin/pratos/${prato.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    nome: prato.nome,
                    descricao: prato.descricao,
                    preco: prato.preco,
                    categoria: prato.categoria,
                    tempo_preparo_min: prato.tempo_preparo_min || 20,
                    estoque: prato.estoque ?? 50,
                    ativo: 1
                })
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao reativar produto.");
            }
            mostrarAvisoAdmin(dados.mensagem);
        }
        await atualizarAdmin();
    } catch (erro) {
        mostrarAvisoAdmin(erro.message, true);
    }
}

if (formEditarPrato) {
    formEditarPrato.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idPrato = document.getElementById("edit-prato-id").value;
        const formData = new FormData(formEditarPrato);
        try {
            const resposta = await fetch(`/api/admin/pratos/${idPrato}`, {
                method: "POST",
                body: formData
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar produto.");
            }
            modalEditarPrato.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (botaoFecharModalPrato) {
    botaoFecharModalPrato.addEventListener("click", () => modalEditarPrato.close());
}

if (formEditarBancada) {
    formEditarBancada.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idBancada = document.getElementById("edit-bancada-id").value;
        const payload = Object.fromEntries(new FormData(formEditarBancada).entries());
        try {
            const resposta = await fetch(`/api/bancadas/${idBancada}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar bancada.");
            }
            modalEditarBancada.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (botaoFecharModalBancada) {
    botaoFecharModalBancada.addEventListener("click", () => modalEditarBancada.close());
}

if (formEditarReserva) {
    ["edit-reserva-bancada", "edit-reserva-inicio", "edit-reserva-fim", "edit-reserva-status"].forEach(idCampo => {
        const el = document.getElementById(idCampo);
        if (el) {
            el.addEventListener("input", verificarColisaoNoModalAdmin);
            el.addEventListener("change", verificarColisaoNoModalAdmin);
        }
    });

    formEditarReserva.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idReserva = document.getElementById("edit-reserva-id").value;
        const payload = Object.fromEntries(new FormData(formEditarReserva).entries());
        try {
            const resposta = await fetch(`/api/admin/reservas/${idReserva}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar reserva.");
            }
            modalEditarReserva.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            avisoConflitoModalAdmin.textContent = erro.message;
        }
    });
}

if (botaoFecharModalReserva) {
    botaoFecharModalReserva.addEventListener("click", () => modalEditarReserva.close());
}

if (formEditarPedido) {
    formEditarPedido.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idPedido = document.getElementById("edit-pedido-id").value;
        const payload = Object.fromEntries(new FormData(formEditarPedido).entries());
        try {
            const resposta = await fetch(`/api/admin/pedidos/${idPedido}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar pedido.");
            }
            modalEditarPedido.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (botaoFecharModalPedido) {
    botaoFecharModalPedido.addEventListener("click", () => modalEditarPedido.close());
}

if (formEditarFuncionario) {
    formEditarFuncionario.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idFunc = document.getElementById("edit-func-id").value;
        const payload = Object.fromEntries(new FormData(formEditarFuncionario).entries());
        try {
            const resposta = await fetch(`/api/admin/funcionarios/${idFunc}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar funcionário.");
            }
            modalEditarFuncionario.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (botaoFecharModalFuncionario) {
    botaoFecharModalFuncionario.addEventListener("click", () => modalEditarFuncionario.close());
}

if (formEditarCliente) {
    formEditarCliente.addEventListener("submit", async evento => {
        evento.preventDefault();
        const idCli = document.getElementById("edit-cli-id").value;
        const payload = Object.fromEntries(new FormData(formEditarCliente).entries());
        try {
            const resposta = await fetch(`/api/admin/clientes/${idCli}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao atualizar cliente.");
            }
            modalEditarCliente.close();
            mostrarAvisoAdmin(dados.mensagem);
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (botaoFecharModalCliente) {
    botaoFecharModalCliente.addEventListener("click", () => modalEditarCliente.close());
}

const formNovaBancada = document.getElementById("form-nova-bancada");
if (formNovaBancada) {
    formNovaBancada.addEventListener("submit", async evento => {
        evento.preventDefault();
        const payload = Object.fromEntries(new FormData(formNovaBancada).entries());
        try {
            const resposta = await fetch("/api/admin/bancadas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao cadastrar bancada.");
            }
            mostrarAvisoAdmin(dados.mensagem);
            formNovaBancada.reset();
            await atualizarAdmin();
        } catch (erro) {
            mostrarAvisoAdmin(erro.message, true);
        }
    });
}

if (buscaPratoAdmin) {
    buscaPratoAdmin.addEventListener("input", renderizarListaProdutosAdmin);
}
if (filtroCategoriaAdmin) {
    filtroCategoriaAdmin.addEventListener("change", renderizarListaProdutosAdmin);
}
if (filtroStatusAdmin) {
    filtroStatusAdmin.addEventListener("change", renderizarListaProdutosAdmin);
}

if (filtroReservaBancada) {
    filtroReservaBancada.addEventListener("change", renderizarAgendaReservasAdmin);
}
if (filtroReservaData) {
    filtroReservaData.addEventListener("input", renderizarAgendaReservasAdmin);
}
if (filtroReservaStatus) {
    filtroReservaStatus.addEventListener("change", renderizarAgendaReservasAdmin);
}
if (filtroPedidoStatusAdmin) {
    filtroPedidoStatusAdmin.addEventListener("change", () => renderizarPedidosEAuditoriaAdmin());
}

document.getElementById("form-produto").addEventListener("submit", async evento => {
    evento.preventDefault();
    const form = evento.currentTarget;
    try {
        const resposta = await fetch("/api/admin/pratos", {
            method: "POST",
            body: new FormData(form)
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao cadastrar produto.");
        }
        mostrarAvisoAdmin(dados.mensagem);
        form.reset();
        await atualizarAdmin();
    } catch (erro) {
        mostrarAvisoAdmin(erro.message, true);
    }
});

document.getElementById("form-funcionario").addEventListener("submit", async evento => {
    evento.preventDefault();
    const form = evento.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
        const resposta = await fetch("/api/admin/funcionarios", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao cadastrar funcionário.");
        }
        mensagemFuncionario.textContent = dados.mensagem;
        form.reset();
        await atualizarAdmin();
    } catch (erro) {
        mensagemFuncionario.textContent = erro.message;
    }
});

configurarAbas();
atualizarAdmin();
