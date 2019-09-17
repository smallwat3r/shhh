
$('#secretSender').on('submit',function(event){event.preventDefault();$.ajax({url:'/api/send',data:$('#secretSender').serialize(),type:'POST',success:function(d){alert(d.result);}});});