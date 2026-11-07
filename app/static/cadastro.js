function validarFormulario() { // verifica se o formulario foi preenchido corretamente
    console.log("FUNÇÃO FOI CHAMADA");

    const nome = document.getElementById("nome").value;
    const telefone = document.getElementById("telefone").value;
    const cpf = document.getElementById("cpf").value;
    const dataNascimento = document.getElementById("data_nascimento").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const genero = document.getElementById("genero").value;

    if (
        nome === "" ||
        telefone === "" ||
        cpf === "" ||
        dataNascimento === "" ||
        email === "" ||
        senha === "" ||
        genero === ""
    ) {
        alert("Preencha todos os campos!");
        return false;
    }

    return true;
}