var buy_price
var sell_price
var table = document.getElementById("my_table");
var i;
var buy_price_map = new Map() 
var sell_price_map = new Map() 



function add_new_row_to_table(stock_symbol,eps_array,net_income_array,sales_array){
    var table = document.getElementById("my_table");
    var row = table.insertRow(1);

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    // Add some text to the new cells:
    cell1.innerHTML = stock_symbol;
    cell2.innerHTML = eps_array;
    cell3.innerHTML = net_income_array;
    cell4.innerHTML = sales_array;
}


const Http = new XMLHttpRequest();
const url='http://127.0.0.1:8000/volume_update/';
Http.open("GET", url,true);

Http.send();
Http.addEventListener("readystatechange", function() {
    if (this.readyState === 4) {
        if (Http.status === 200) {
            stock_dict = Http.responseText;
            var stock_dict_parsed = JSON.parse(stock_dict);

            for (var key in stock_dict_parsed){
                add_new_row_to_table( key, stock_dict_parsed[key][0], stock_dict_parsed[key][1], stock_dict_parsed[key][2]);

              }
        }

    }
});





