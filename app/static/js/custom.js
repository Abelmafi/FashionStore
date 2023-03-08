function recordUserBehavior(productId, behaviorType) {
        fetch('/record-behavior', {
          method: 'POST',
          body: JSON.stringify({
            'product_id': productId,
            'behavior_type': behaviorType
          }),
          headers: {
            'Content-Type': 'application/json'
          }
        });
}

const input = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");

const expand = () => {
  searchBtn.classList.toggle("close");
  input.classList.toggle("square");
};

searchBtn.addEventListener("click", expand);
