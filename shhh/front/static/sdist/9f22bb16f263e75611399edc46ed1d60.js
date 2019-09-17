
$('#secretSender').on('submit',function(event){event.preventDefault();$.ajax({url:'/api/send',data:$('#secretSender').serialize(),type:'POST',complete:function(data){console.log(data);}});});