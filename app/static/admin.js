const moeda = valor => Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const mensagem = document.getElementById('mensagem-admin');
const mensagemFuncionario = document.getElementById('mensagem-funcionario');

async function atualizarAdmin() {
    try {
        const [r1, r2] = await Promise.all([fetch('/api/admin/pratos'), fetch('/api/admin/relatorio')]);
        if (!r1.ok || !r2.ok) throw new Error('Erro ao carregar painel');
        const pratos = await r1.json(), resumo = await r2.json();
        const lista = document.getElementById('produtos-admin');
        lista.replaceChildren();
        pratos.forEach(prato => {
            const div = document.createElement('article');
            div.className = 'produto-admin';
            const titulo = document.createElement('strong');
            titulo.textContent = `${prato.nome} — ${moeda(prato.preco)} (${prato.categoria})`;
            const editar = document.createElement('button');
            editar.textContent = 'Editar';
            editar.onclick = () => editarProduto(prato);
            const excluir = document.createElement('button');
            excluir.textContent = prato.ativo ? 'Desativar' : 'Indisponível';
            excluir.disabled = !prato.ativo;
            excluir.onclick = async () => {
                if (!confirm('Desativar este produto?')) return;
                await fetch(`/api/admin/pratos/${prato.id}`, { method: 'DELETE' });
                atualizarAdmin();
            };
            div.append(titulo, editar, excluir);
            lista.append(div);
        });
        document.getElementById('resumo-admin').textContent = `${resumo.pedidos} pedidos | Total: ${moeda(resumo.faturamento)}`;
        const listaFuncionarios = document.getElementById('funcionarios-admin');
        listaFuncionarios.replaceChildren();
        if (!resumo.funcionarios.length) {
            listaFuncionarios.textContent = 'Nenhum funcionário cadastrado';
        } else {
            resumo.funcionarios.forEach(f => {
                const card = document.createElement('article');
                card.className = 'produto-admin';
                const info = document.createElement('strong');
                info.textContent = `${f.nome} — ${f.email} (${f.tipo})`;
                card.append(info);
                listaFuncionarios.append(card);
            });
        }
    } catch (e) {
        mensagem.textContent = e.message;
    }
}

async function editarProduto(prato) {
    const nome = prompt('Nome:', prato.nome);
    if (nome === null) return;
    const descricao = prompt('Descrição:', prato.descricao);
    if (descricao === null) return;
    const preco = prompt('Preço:', prato.preco);
    if (preco === null) return;
    const r = await fetch(`/api/admin/pratos/${prato.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, descricao, preco, categoria: prato.categoria, ativo: prato.ativo })
    });
    const dados = await r.json();
    mensagem.textContent = dados.mensagem || dados.erro;
    atualizarAdmin();
}

document.getElementById('form-produto').addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.currentTarget;
    try {
        const r = await fetch('/api/admin/pratos', { method: 'POST', body: new FormData(form) });
        const dados = await r.json();
        if (!r.ok) throw new Error(dados.erro);
        mensagem.textContent = dados.mensagem;
        form.reset();
        await atualizarAdmin();
    } catch (erro) {
        mensagem.textContent = erro.message;
    }
});

document.getElementById('form-funcionario').addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
        const r = await fetch('/api/admin/funcionarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const dados = await r.json();
        if (!r.ok) throw new Error(dados.erro);
        mensagemFuncionario.textContent = dados.mensagem;
        form.reset();
        await atualizarAdmin();
    } catch (erro) {
        mensagemFuncionario.textContent = erro.message;
    }
});

atualizarAdmin();