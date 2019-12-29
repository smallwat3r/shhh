
$(document).ready(function(){$('#secretSender').on('submit',function(event){event.preventDefault();blockUI();$.ajax({url:'/api/send',data:$('#secretSender').serialize(),type:'POST',success:function(d){$('#linkPop').fadeIn(1000);var domain=window.location.hostname
if(domain=='0.0.0.0'){$('#linkDetail').empty().append(window.location.hostname+':5000/read?slug='+d.slug);}else{$('#linkDetail').empty().append(window.location.hostname+'/read?slug='+d.slug);}
$('#linkExpire').empty().append(d.expires);},complete:function(){$.unblockUI();}});});});