$('#myTab a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
})


$('.carousel').carousel({
  interval: 2000
})