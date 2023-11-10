function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            $(".image-upload-wrap").hide();

            $("#aud").attr("src", e.target.result);

            $(".image-title").html(input.files[0].name);
            
            $(".image-title-wrap").show();
            
        };

        // reader.readAsDataURL(input.files[0]);
    }
    else {
        Upload();
    }
}

function Upload() {
    $(".file-upload-input").replaceWith($(".file-upload-input").clone());
    $(".file-upload-content").hide();
    $(".image-upload-wrap").show();
}
$(".image-upload-wrap").bind("dragover", function() { $(".image-upload-wrap").addClass("image-dropping"); });
$(".image-upload-wrap").bind("dragleave", function() { $(".image-upload-wrap").removeClass("image-dropping"); });
