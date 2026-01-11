
let images = [$("#image_1"), $("#image_2"), $("#image_3")];

$(document).ready(function () {
  /*change the main image when clicking on thumbnails*/
  images.forEach(function (image) {
    image.click(function () {
      images.forEach(function (img) {
        img.removeClass("active");
      });
      $(this).addClass("active");
      $("#main_image").attr("src", $(this).data("url"));
    });
  });
});

/*change the main image every 5 seconds*/
$(document).ready(function () {
  let currentImage = 0;

  setInterval(function () {
    $("#main_image").attr("src", images[currentImage].data("url"));
    images.forEach(function (img) {
        img.removeClass("active");
      });
    images[currentImage].addClass("active");
    currentImage = (currentImage + 1) % images.length;
  }, 5000);
});
