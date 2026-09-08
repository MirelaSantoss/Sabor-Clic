function validarFormulario() { // verifica se o formulario foi preenchido corretamente
    console.log("FUNÇÃO FOI CHAMADA");
    
    const nome = document.getElementById("nome").value; // procura no HTML o elemento que tenha o mesmo nome do id
    const telefone = document.getElementById("telefone").value; // value - pega o que foi digitado no campo
    const cpf = document.getElementById("cpf").value;
    const dataNascimento = document.getElementById("data_nascimento").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const genero = document.getElementById("genero").value;

    const rua = document.getElementById("rua").value;
    const numero = document.getElementById("numero").value;
    const bairro = document.getElementById("bairro").value;
    const cidade = document.getElementById("cidade").value;
    const estado = document.getElementById("estado").value;
    const cep = document.getElementById("cep").value;

    if (
        nome === "" || // verifica se algum campo está vazio
        telefone === "" ||
        cpf === "" ||
        dataNascimento === "" ||
        email === "" ||
        senha === "" ||
        genero === "" ||
        rua === "" ||
        numero === "" ||
        bairro === "" ||
        cidade === "" ||
        estado === "" ||
        cep === ""
    ) {
        alert("Preencha todos os campos!"); // se algum estiver vazio, aparece essa msg na tela
        return false; // se estiver não continua o envio do formulario
    }
}