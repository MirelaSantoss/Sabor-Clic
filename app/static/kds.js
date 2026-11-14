const kds=document.getElementById('kds');
const grupos=[['Aguardando','Pedidos Novos'],['Iniciando Preparo','Pedidos em Andamento'],['Pronto para Entrega','Prontos para Entrega']];
async function mostrarPedidos(){try{const r=await fetch('/pedidos');const dados=await r.json();if(!r.ok)throw Error(dados.erro||'Falha ao carregar pedidos');kds.replaceChildren();
 grupos.forEach(([status,titulo])=>{const coluna=document.createElement('section');coluna.className='kds-coluna';const h=document.createElement('h2');h.textContent=titulo;coluna.append(h);
 dados.filter(p=>p.status===status).forEach(p=>{const card=document.createElement('article');card.className='pedido-kds';const h3=document.createElement('h3');h3.textContent=`#${p.id} · ${p.cliente_nome||'Cliente'}`;card.append(h3);
 (p.itens||[]).forEach(item=>{const linha=document.createElement('p');linha.textContent=`${item.quantidade}× ${item.nome}`;card.append(linha)});
 const hora=document.createElement('small');hora.textContent=p.data_pedido||'';card.append(hora);
 if(status!=='Pronto para Entrega'){const b=document.createElement('button');b.className='botao';b.textContent=status==='Aguardando'?'Iniciar preparo':'Pronto para entrega';b.onclick=()=>avancar(p);card.append(b)}coluna.append(card)});
 kds.append(coluna)});
 }catch(e){kds.textContent=e.message}}
async function avancar(p){const status=p.status==='Aguardando'?'Iniciando Preparo':'Pronto para Entrega';try{const r=await fetch(`/pedidos/${p.id}/status`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})});if(!r.ok)throw Error('Não foi possível alterar o pedido');await mostrarPedidos()}catch(e){alert(e.message)}}
function atualizarRelogio(){document.getElementById('relogio').textContent=new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}
atualizarRelogio();setInterval(atualizarRelogio,30000);mostrarPedidos();setInterval(mostrarPedidos,15000);