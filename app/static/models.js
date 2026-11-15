// Modelos ES6+ do front-end: encapsulamento, herança e método estático.
class ItemPedido {
 #quantidade;
 constructor(id, nome, preco, quantidade=1){
  this.id=id;this.nome=nome;this.preco=Number(preco);this.quantidade=quantidade;
 }
 get quantidade(){return this.#quantidade}
 set quantidade(valor){
  if(!Number.isInteger(Number(valor))||Number(valor)<1)throw Error('Quantidade inválida');
  this.#quantidade=Number(valor);
 }
 get subtotal(){return this.preco*this.#quantidade}
 static formatarPreco(valor){return Number(valor).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})}
}
class ItemCarrinho extends ItemPedido {
 constructor(dados){super(dados.id,dados.nome,dados.preco,dados.quantidade);this.observacoes=dados.observacoes||''}
 toJSON(){return {id:this.id,nome:this.nome,preco:this.preco,quantidade:this.quantidade,observacoes:this.observacoes}}
}
window.ItemCarrinho=ItemCarrinho;
