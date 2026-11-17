const mensagemAdmin = document.getElementById("mensagem-admin");
const mensagemFuncionario = document.getElementById("mensagem-funcionario");
const listaProdutosAdmin = document.getElementById("produtos-admin");
const resumoAdmin = document.getElementById("resumo-admin");
const listaFuncionariosAdmin = document.getElementById("funcionarios-admin");
const listaBancadasAdmin = document.getElementById("bancadas-admin");

async function atualizarAdmin() {
    try {
        const [r1, r2] = await Promise.all([
            fetch("/api/admin/pratos"),
            fetch("/api/admin/relatorio")
        ]);

        if (!r1.ok || !r2.ok) {
            throw new Error("Erro ao carregar dados do painel administrativo.");
        }

        const pratosBrutos = await r1.json();
        const resumo = await r2.json();

        listaProdutosAdmin.replaceChildren();
        pratosBrutos.forEach(item => {
            const prato = new Prato(item);
            const card = document.createElement("article");
            card.className = "produto-admin";

            const titulo = document.createElement("strong");
            const sufixoStatus = prato.ativo ? "" : " [Inativo]";
            titulo.textContent = `${prato.nome} — ${prato.precoFormatado} (${prato.categoria})${sufixoStatus}`;

            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.textContent = "Editar";
            botaoEditar.onclick = () => editarProduto(item);

            const botaoStatus = document.createElement("button");
            botaoStatus.type = "button";
            botaoStatus.textContent = prato.ativo ? "Desativar" : "Reativar";
            botaoStatus.onclick = () => alternarStatusProduto(item);

            card.append(titulo, botaoEditar, botaoStatus);
            listaProdutosAdmin.append(card);
        });

        resumoAdmin.textContent = `${resumo.pedidos} pedidos realizados | Faturamento total: ${Prato.formatarMoeda(resumo.faturamento)}`;

        listaFuncionariosAdmin.replaceChildren();
        const funcionarios = (resumo.funcionarios || []).map(f => new Usuario(f));
        if (funcionarios.length === 0) {
            listaFuncionariosAdmin.textContent = "Nenhum funcionário cadastrado.";
        } else {
            funcionarios.forEach(funcionario => {
                const card = document.createElement("article");
                card.className = "produto-admin";
                const info = document.createElement("strong");
                info.textContent = `${funcionario.nome} — ${funcionario.email} (${funcionario.tipo})`;
                card.append(info);
                listaFuncionariosAdmin.append(card);
            });
        }

        if (listaBancadasAdmin && Array.isArray(resumo.bancadas)) {
            listaBancadasAdmin.replaceChildren();
            resumo.bancadas.forEach(dadosBancada => {
                const bancada = new Bancada(dadosBancada);
                const card = document.createElement("article");
                card.className = "produto-admin";

                const info = document.createElement("strong");
                info.textContent = `${bancada.codigo} — Hora: ${bancada.valorHoraFormatado} | Caução: ${bancada.valorCaucaoFormatado} (${bancada.statusOperacional})`;

                const botaoConfig = document.createElement("button");
                botaoConfig.type = "button";
                botaoConfig.textContent = "Definir preço/caução";
                botaoConfig.onclick = () => editarBancada(dadosBancada);

                card.append(info, botaoConfig);
                listaBancadasAdmin.append(card);
            });
        }
    } catch (erro) {
        if (mensagemAdmin) {
            mensagemAdmin.textContent = erro.message;
        }
    }
}

async function alternarStatusProduto(prato) {
    try {
        if (prato.ativo) {
            if (!confirm("Deseja desativar este produto do cardápio?")) {
                return;
            }
            const resposta = await fetch(`/api/admin/pratos/${prato.id}`, {
                method: "DELETE"
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao desativar produto.");
            }
            mensagemAdmin.textContent = dados.mensagem;
        } else {
            const resposta = await fetch(`/api/admin/pratos/${prato.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    nome: prato.nome,
                    descricao: prato.descricao,
                    preco: prato.preco,
                    categoria: prato.categoria,
                    ativo: 1
                })
            });
            const dados = await resposta.json();
            if (!resposta.ok) {
                throw new Error(dados.erro || "Erro ao reativar produto.");
            }
            mensagemAdmin.textContent = dados.mensagem;
        }
        await atualizarAdmin();
    } catch (erro) {
        mensagemAdmin.textContent = erro.message;
    }
}

async function editarProduto(prato) {
    const nome = prompt("Nome do prato (3 a 120 caracteres):", prato.nome);
    if (nome === null) {
        return;
    }
    const descricao = prompt("Descrição:", prato.descricao);
    if (descricao === null) {
        return;
    }
    const preco = prompt("Preço (R$):", prato.preco);
    if (preco === null) {
        return;
    }
    const categoria = prompt("Categoria (Pratos, Bebidas, Combos, Sobremesas):", prato.categoria || "Pratos");
    if (categoria === null) {
        return;
    }

    try {
        const resposta = await fetch(`/api/admin/pratos/${prato.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nome,
                descricao,
                preco,
                categoria,
                ativo: prato.ativo
            })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao atualizar produto.");
        }
        mensagemAdmin.textContent = dados.mensagem;
        await atualizarAdmin();
    } catch (erro) {
        mensagemAdmin.textContent = erro.message;
    }
}

async function editarBancada(bancada) {
    const valorHora = prompt(`Valor por hora para ${bancada.cod_identificacao} (R$):`, bancada.valor_hora);
    if (valorHora === null) {
        return;
    }
    const valorCaucao = prompt(`Valor de caução para ${bancada.cod_identificacao} (R$):`, bancada.valor_caucao);
    if (valorCaucao === null) {
        return;
    }
    const statusOperacional = prompt(
        "Status operacional (DISPONIVEL, MANUTENCAO, INATIVA):",
        bancada.status_operacional || "DISPONIVEL"
    );
    if (statusOperacional === null) {
        return;
    }

    try {
        const resposta = await fetch(`/api/bancadas/${bancada.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                valor_hora: valorHora,
                valor_caucao: valorCaucao,
                status_operacional: statusOperacional
            })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            throw new Error(dados.erro || "Erro ao atualizar bancada.");
        }
        mensagemAdmin.textContent = dados.mensagem;
        await atualizarAdmin();
    } catch (erro) {
        mensagemAdmin.textContent = erro.message;
    }
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
        mensagemAdmin.textContent = dados.mensagem;
        form.reset();
        await atualizarAdmin();
    } catch (erro) {
        mensagemAdmin.textContent = erro.message;
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

atualizarAdmin();
