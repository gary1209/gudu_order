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
    let p_name = $(this).parent().parent().attr('data-pname');
    let num = parseInt($('input[name="quant['+p_id+']"]').val());
    added_products[p_id]={'p_name': p_name, 'num': num};
});

$(document).on('click', '.remove-product', function(){
    let p_id = $(this).parent().attr('data-pid');
    console.log(p_id);
    delete added_products[p_id];
    $(this).parent().remove();
})

$('#order').on('click', function(){
    if(!table_is_selected()){
        return;
    }
    // [TODO] check if input value is integer
    $('.modal-body').empty();
    $('#order_d_name').text($('select').find('option:selected').text());
    $.each(added_products, function(key, value){
        $('.modal-body').append('<div class="row product-row" data-pid="'+ key +'" data-pname="'+ value['p_name'] +'">\
                <span class="col-8">'+ value['p_name'] +'</span>\
                <span class="col-2">'+ value['num'] +'</span>\
                <div class="btn btn-danger remove-product">x</div>\
            </div>')});
    $('#order-conf').show();
    $('#order_modal').modal('show');
});

$('#order-conf').on('click', function(){
    let d_id = parseInt($('select').val());
    $.ajax({
        url: order_url,
        type: 'POST',
        contentType: "application/json",
        // dataType: 'json',
        processData : false,
        data: JSON.stringify({'d_id': d_id, 'products': added_products}),
        success: function(res){
            console.log(res);
            alert('點餐完成');
            location.reload();
        }
    })
});

$('#check_order').on('click', function(){
    if(!table_is_selected()){
        return;
    }
    let d_id = parseInt($('select').val());
    $('.modal-body').empty();
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
            $('#order-conf').hide();
            $('#order_modal').modal('show');
        }
    })

})
