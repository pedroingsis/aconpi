const loaderOut = document.querySelector("#loader-out");
function fadeOut(element) {
  let opacity = 1;
  const timer = setInterval(function () {
    if (opacity <= 0.1) {
      clearInterval(timer);
      element.style.display = "none";
    }
    element.style.opacity = opacity;
    opacity -= opacity * 0.1;
  }, 50);
}
fadeOut(loaderOut);


function eliminarContrato(id_contrato) {
  if (confirm("¿Estas seguro que deseas Eliminar el contrato?")) {
    let url = `/borrar-contrato/${id_contrato}`;
    if (url) {
      window.location.href = url;
    }
  }
}

function eliminarInnovacion(id_innovacion) {
  console.log("Intentando eliminar la innovación con ID:", id_innovacion);
  if (confirm("¿Estas seguro que deseas Eliminar el registro?")) {
    let url = `/borrar-innovacion/${id_innovacion}`;
    if (url) {
      window.location.href = url;
    }
  }
}

function eliminarPercepcion(id_percepcion) {
  console.log("Intentando eliminar la percepcion con ID:", id_percepcion);
  if (confirm("¿Estas seguro que deseas Eliminar el registro?")) {
    let url = `/borrar-percepcion/${id_percepcion}`;
    if (url) {
      window.location.href = url;
    }
  }
}