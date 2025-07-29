window.addEventListener("DOMContentLoaded", () => {
  console.log("Bank site loaded!");

  // You can add interactive effects here
  const title = document.querySelector(".title");
  title.addEventListener("mouseover", () => {
    title.style.color = "#ff6600";
  });
  title.addEventListener("mouseout", () => {
    title.style.color = "white";
  });
});
