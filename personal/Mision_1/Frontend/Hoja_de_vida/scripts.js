function downloadPDF() {
  const element = document.querySelector("#pdf-content");

  console.log("Si ingresooooo");
  console.log(element);
  const opt = {
    margin: [-15, -5, -10, -5], //[arriba, izquierda, abajo, derecha] en mn
    filename: "Hoja_de_Vida_Jhoann_Reyes.pdf",
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, arroTrain: false, scrollY: 0 },
    jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
  }; 
    html2pdf().set(opt).from(element).save();
}
