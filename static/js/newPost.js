const addPost = () => {
  document.getElementById("add").style.display = "flex";
  document.getElementById("posts").style.display = "none";
  document.getElementById("main").style.height = "100vh";
};

const Posts = () => {
  document.getElementById("add").style.display = "none";
  document.getElementById("posts").style.display = "flex";
  document.getElementById("main").style.height = "auto";
};
