const cardapio=document.getElementById('cardapio');
const dinheiro=valor=>Number(valor).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
let todos=[];
class Produto{constructor(dados){Object.assign(this,dados)} get precoFormatado(){return dinheiro(this.preco)} }
async function mostrarCardapio(){try{const resposta=await fetch('/api/pratos');if(!resposta.ok)throw Error('Erro ao carregar cardápio');todos=(await resposta.json()).map(x=>new Produto(x));renderizar();}catch(e){cardapio.textContent=e.message}}
function renderizar(){const busca=document.getElementById('pesquisa').value.toLowerCase();cardapio.replaceChildren();
 for(const categoria of ['Pratos','Bebidas','Combos','Sobremesas']){
  const itens=todos.filter(p=>(p.categoria||'Pratos')===categoria&&p.nome.toLowerCase().includes(busca));
  const sec=document.createElement('section');sec.id=categoria;const h=document.createElement('h2');h.textContent=categoria;sec.append(h);
  const grade=document.createElement('div');grade.className='grade-produtos';
  itens.forEach(prato=>{const art=document.createElement('article');art.className='produto';
   if(prato.imagem){const img=document.createElement('img');img.src='/static/'+prato.imagem;img.alt=prato.nome;art.append(img)}else{const foto=document.createElement('div');foto.className='foto-vazia';foto.textContent='🍽';art.append(foto)}
   const titulo=document.createElement('h3');titulo.textContent=prato.nome;const desc=document.createElement('p');desc.textContent=prato.descricao;const preco=document.createElement('strong');preco.textContent=prato.precoFormatado;
   const botao=document.createElement('button');botao.className='botao';botao.textContent='Ver detalhes';botao.onclick=()=>abrirDetalhes(prato);
   art.append(titulo,desc,preco,botao);grade.append(art)});
  if(!itens.length){const vazio=document.createElement('p');vazio.textContent='Nenhum produto nesta categoria.';grade.append(vazio)}sec.append(grade);cardapio.append(sec);
 }}
function abrirDetalhes(prato){const modal=document.getElementById('detalhes');const corpo=document.getElementById('detalhes-corpo');corpo.replaceChildren();
 const titulo=document.createElement('h2');titulo.textContent=prato.nome;const desc=document.createElement('p');desc.textContent=prato.descricao;
 const preco=document.createElement('strong');preco.textContent=prato.precoFormatado;
 const quantidade=document.createElement('input');quantidade.type='number';quantidade.min=1;quantidade.value=1;
 const observacoes=document.createElement('textarea');observacoes.placeholder='Observações (opcional)';
 const adicionar=document.createElement('button');adicionar.className='botao';adicionar.textContent='Adicionar ao carrinho';adicionar.onclick=()=>{adicionarCarrinho(prato,Number(quantidade.value),observacoes.value);modal.close()};
 corpo.append(titulo,desc,preco,quantidade,observacoes,adicionar);modal.showModal();}
function adicionarCarrinho(prato,quantidade,observacoes){if(!Number.isInteger(quantidade)||quantidade<1)return alert('Quantidade inválida');
 const carrinho=JSON.parse(localStorage.getItem('sabor_clic_carrinho')||'[]');const existente=carrinho.find(x=>x.id===prato.id&&x.observacoes===observacoes);
 if(existente)existente.quantidade+=quantidade;else carrinho.push({id:prato.id,nome:prato.nome,preco:prato.preco,imagem:prato.imagem,quantidade,observacoes});
 localStorage.setItem('sabor_clic_carrinho',JSON.stringify(carrinho));alert('Produto adicionado ao carrinho!')}
document.getElementById('pesquisa').addEventListener('input',renderizar);
document.getElementById('fechar-detalhes').onclick=()=>document.getElementById('detalhes').close();mostrarCardapio();