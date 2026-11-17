function validarFormulario() {
    const nome = document.getElementById("nome").value.trim();
    const telefone = document.getElementById("telefone").value.trim();
    const cpf = document.getElementById("cpf").value.trim();
    const dataNascimento = document.getElementById("data_nascimento").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value;
    const genero = document.getElementById("genero").value.trim();

    if (!nome || !telefone || !cpf || !dataNascimento || !email || !senha || !genero) {
        alert("Preencha todos os campos obrigatórios!");
        return false;
    }

    if (typeof Usuario !== "undefined" && !Usuario.validarEmail(email)) {
        alert("Informe um e-mail válido com no máximo 120 caracteres.");
        return false;
    }

    if (typeof Usuario !== "undefined" && !Usuario.validarSenha(senha)) {
        alert("A senha deve ter pelo menos 8 caracteres, misturando letras e números.");
        return false;
    }

    return true;
}
