var added_products = {};

function table_is_selected(){
    if($('select').val() == null){
        alert('請選桌號');
        return false;
    }
    return true
}

$('.btn-number').click(function(e){
    e.preventDefault();
    
    fieldName = $(this).attr('data-field');
    type      = $(this).attr('data-type');
    var input = $("input[name='"+fieldName+"']");
    var currentVal = parseInt(input.val());
    if (!isNaN(currentVal)) {
        if(type == 'minus') {
            
            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
            } 
            if(parseInt(input.val()) == input.attr('min')) {
                $(this).attr('disabled', true);
            }

        } else if(type == 'plus') {

            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(this).attr('disabled', true);
            }

        }
    } else {
        input.val(0);
    }
});
$('.input-number').focusin(function(){
   $(this).data('oldValue', $(this).val());
});
$('.input-number').change(function() {
    
    minValue =  parseInt($(this).attr('min'));
    maxValue =  parseInt($(this).attr('max'));
    valueCurrent = parseInt($(this).val());
    
    name = $(this).attr('name');
    if(valueCurrent >= minValue) {
        $(".btn-number[data-type='minus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the minimum value was reached');
        $(this).val($(this).data('oldValue'));
    }
    if(valueCurrent <= maxValue) {
        $(".btn-number[data-type='plus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the maximum value was reached');
        $(this).val($(this).data('oldValue'));
    }
    let p_id = parseInt($(this).parent().parent().attr('data-pid'));

    if(valueCurrent != 0){
        let p_name = $(this).parent().parent().attr('data-pname');
        let p_price = parseInt($(this).parent().parent().attr('data-pprice'));
        let checkbox = $(this).parent().parent().find('input[type=checkbox]');
        if(checkbox.prop("checked") == true){
            p_price = 0;
        }
        added_products[p_id]={'p_name': p_name, 'num': valueCurrent, 'price': p_price};
        
    }else{
        delete added_products[p_id];
    }
});

$(document).on('click', '.remove-product', function(){
    let p_id = parseInt($(this).parent().attr('data-pid'));
    console.log(p_id);
    delete added_products[p_id];
    $("input[name='quant["+p_id+"]']").val(0).change();
    $(this).parent().remove();
})

$('#order').on('click', function(){
    if(!table_is_selected()){
        return;
    }
    if($.isEmptyObject(added_products)){
        alert('請選商品');
        return;
    }

    $('.modal-body').empty();
    $('#order_d_name').text($('select').find('option:selected').text());
    $.each(added_products, function(key, value){
        $('.modal-body').append('<div class="row product-row" data-pid="'+ key +'" data-pname="'+ value['p_name'] +'">\
                <span class="col-6">'+ value['p_name'] +'</span>\
                <span class="col-2">x'+ value['num'] +'</span>\
                <span class="col-2">$'+ value['price'] +'</span>\
                <div class="btn btn-danger remove-product">x</div>\
            </div>')});
    $('#order_conf').show();
    $('#note_row').show();
    $('#order_conf').attr('disabled', false);
    $('#order_modal').modal('show');
});

$('#order_conf').on('click', function(){
    if($.isEmptyObject(added_products)){
        alert('請選商品');
        $('#order_modal').modal('hide');
        return;
    }
    $('#order_conf').attr('disabled', true);
    let d_id = parseInt($('select').val());
    let note = $('#note').val();
    let products = []
    $.each(added_products, function(key, value){
        products.push({
            'id': parseInt(key),
            'name': value['p_name'],
            'num': value['num'],
            'price': value['price']})
    });

    $.ajax({
        url: order_url,
        type: 'POST',
        contentType: "application/json",
        dataType: 'json',
        processData : false,
        data: JSON.stringify({'d_id': d_id, 'products': products, 'note': note}),
        success: function(res){
            console.log(res);
            if(res['state'] == 'ok'){
                alert('點餐完成');
                location.reload();
            }else{
                alert(res['reason']);
                $('#order_modal').modal('hide');
                if(res['state'] == 'printer error'){
                    window.location.href = error_page_url;
                }
            }
        },
        error: function(){
            $('#order_conf').attr('disabled', false);
        }
    });
});

$('#check_order').on('click', function(){
    if(!table_is_selected()){
        return;
    }
    let d_id = parseInt($('select').val());
    $('.modal-body').empty();
    $('#note_row').hide();
    $('#order_d_name').text($('select').find('option:selected').text());
    $.ajax({
        url: check_order_url,
        type: 'POST',
        contentType: "application/json",
        dataType: 'json',
        processData : false,
        data: JSON.stringify({'d_id': d_id}),
        success: function(res){
            $.each(res['details'], function(idx, detail){
                $('.modal-body').append('<div class="row product-row">\
                    <span class="col-6">'+ detail[0] +'</span>\
                    <span class="col-2">x'+ detail[2] +'</span>\
                    <span class="col-4 ">'+ detail[3] +'</span>\
                </div>')});
            $('#order_conf').hide();
            $('#order_modal').modal('show');
        }
    })
})

$('#add_spice').on('click', function(){
    $('#note').val($('#note').val()+'加辣');
})

$('#no_spice').on('click', function(){
    $('#note').val($('#note').val()+'不辣');
})

$('.free').on('change', function(){
    let p_id = parseInt($(this).parent().parent().attr('data-pid'));
    if($(this).prop("checked") == true){
        added_products[p_id]['price'] = 0;
    }else{
        added_products[p_id]['price'] = parseInt($(this).parent().parent().attr('data-pprice'));
    }
    
})
