
function predicateChange() {

    var e = document.getElementById(event.srcElement.id);
    var value = e.options[e.selectedIndex].value;
    if (value == "boolean" || value == "trendUpward" || value == "trendUpwardStrict" || value == "trendDownward" || value == "trendDownwardStrict") {
        console.log("changing");
        var id = event.srcElement.id.charAt(event.srcElement.id.length - 1);
        string_id = "input[name='comp_value_" + id + "']";
        console.log(string_id);
        $(string_id).prop("disabled", true);
    } else {
        var id = event.srcElement.id.charAt(event.srcElement.id.length - 1);
        string_id = "input[name='comp_value_" + id + "']";
        console.log(string_id);
        $(string_id).prop("disabled", false);
    }
}

$(document).ready(function () {
    $("body").on("click", ".add_new_frm_field_btn", function () {
        console.log("clicked");
        var index = $(".form_field_outer1").find(".form_field_outer_row").length + 1;
        $(".form_field_outer1").append(`
                
                <div class="row form_field_outer_row">
                        <div class="col-md-12">
                            <label>Predicate Description</label>
                            <div class="form-group col-md-12">
                                <input type="text" class="form-control w_90" name="pred_description_${index}"
                                    id="pred_description_${index}" placeholder="Enter predicate descrition." />
                            </div>
                        </div>
                        <div class="col-md-6">
                            <label>Predicate Name</label>
                        </div>
                        <div class="col-md-4">
                            <label>Predicate Logic</label>
                        </div>
                        <div class="col-md-2">
                            <label>Comparison Value</label>
                        </div>
                        <div class="col-md-12">
                            <div class="col-md-12 ">
                                <div class="row ">
                                    <div class="form-group col-md-6">
                                        <input type="text" class="form-control w_90" name="pred_name_${index}" id="pred_name_${index}"
                                            placeholder="Enter predicate name." />
                                    </div>
                                    <div class="form-group col-md-4">
                                        <select name="pred_type_${index}" id="pred_type_${index}" class="form-control" onchange="predicateChange()">
                                            <option>--Select predicate logic--</option>
                                                <option>equal</option>
                                                <option>notEqual</option>
                                                <option>bigger</option>
                                                <option>biggerEqual</option>
                                                <option>smaller</option>
                                                <option>smallerEqual</option>
                                                <option>boolean</option>
                                                <option>trendUpward</option>
                                                <option>trendUpwardStrict</option>
                                                <option>trendDownward</option>
                                                <option>trendDownwardStrict</option>
                                        </select>
                                    </div>
                                    <div class="form-group col-md-2">
                                        <input type="text" class="form-control w_90" name="comp_value_${index}"
                                            id="comp_value_${index}" placeholder="Enter comparison value." />
                                    </div>

                                </div>
                                <button class="btn_round remove_node_btn_frm_field" disabled>
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `);

        $(".form_field_outer1").find(".remove_node_btn_frm_field:not(:first)").prop("disabled", false);
        $(".form_field_outer1").find(".remove_node_btn_frm_field").first().prop("disabled", true);
    });
});


///======Clone method
$(document).ready(function () {
    $("body").on("click", ".add_node_btn_frm_field", function (e) {
        var index = $(e.target).closest(".form_field_outer").find(".form_field_outer_row").length + 1;
        var cloned_el = $(e.target).closest(".form_field_outer_row").clone(true);

        $(e.target).closest(".form_field_outer").last().append(cloned_el).find(".remove_node_btn_frm_field:not(:first)").prop("disabled", false);

        $(e.target).closest(".form_field_outer").find(".remove_node_btn_frm_field").first().prop("disabled", true);


        //change id
        $(e.target).closest(".form_field_outer").find(".form_field_outer_row").last().find("input[type='text']").attr("id", "mobileb_no_" + index);

        $(e.target).closest(".form_field_outer").find(".form_field_outer_row").last().find("select").attr("id", "no_type_" + index);

        console.log(cloned_el);
        //count++;
    });
});


$(document).ready(function () {
    //===== delete the form fieed row
    $("body").on("click", ".remove_node_btn_frm_field", function () {
        $(this).closest(".form_field_outer_row").remove();
        console.log("success");
    });
});

// ----------------------------------------------------------

$(document).ready(function () {
    $("body").on("click", ".add_new_frm_field_btn2", function () {


        var e = document.getElementById("measurement_select");
        var index = e.selectedIndex;

        if (index == 1) {
            console.log("clicked");
            var index = $(".form_field_outer2").find(".form_field_outer_row").length + 1;
            $(".form_field_outer2").append(`
                
                        <div class="row form_field_outer_row">
                            <div class="col-md-12 ">
                                <div class="row ">
                                    <div class="col-md-4">
                                        <label>Measurement Name</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_name_${index}"
                                                id="measurement_name_${index}" placeholder="Enter Measurement Name." />
                                        </div>

                                    </div>
                                    <div class="form-group col-md-8">
                                        <label>Measurement Query</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_query_${index}"
                                                id="measurement_query_${index}" placeholder="Enter Measurement Query." />
                                        </div>

                                    </div>
                                </div>
                                <button class="btn_round remove_node_btn_frm_field2" disabled>
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </div>
                `);
        }
        else if (index == 2) {
            console.log("clicked");
            var index = $(".form_field_outer2").find(".form_field_outer_row").length + 1;
            $(".form_field_outer2").append(`
                
                        <div class="row form_field_outer_row">
                            <div class="col-md-12 ">
                                <div class="row ">
                                    <div class="col-md-4">
                                        <label>Measurement Name</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_name_${index}"
                                                id="measurement_name_${index}" placeholder="Enter Measurement Name." />
                                        </div>

                                    </div>
                                    <div class="form-group col-md-8">
                                        <label>Measurement Query</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_query_${index}"
                                                id="measurement_query_${index}" placeholder="Enter Measurement Query." />
                                        </div>

                                    </div>

                                    <div class="col-md-4">
                                        <label>Start Time</label>
                                        <input type="text" class="form-control w_90" name="start_time_${index}"
                                            id="start_time_${index}" placeholder="Start Time" />
                                    </div>
                                    <div class="col-md-4">
                                        <label>End Time</label>
                                        <input type="text" class="form-control w_90" name="end_time_${index}" id="end_time_${index}"
                                            placeholder="End Time" />
                                    </div>
                                    <div class="col-md-4">
                                        <label>Steps</label>
                                        <input type="text" class="form-control w_90" name="steps_${index}" id="steps_${index}"
                                            placeholder="Steps" />
                                    </div>

                                </div>
                                <button class="btn_round remove_node_btn_frm_field2" disabled>
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </div>
                `);
        }
        if (index == 3) {
            console.log("clicked");
            var index = $(".form_field_outer2").find(".form_field_outer_row").length + 1;
            $(".form_field_outer2").append(`
                
                        <div class="row form_field_outer_row">
                            <div class="col-md-12 ">
                                <div class="row ">
                                    <div class="col-md-4">
                                        <label>Measurement Name</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_name_${index}"
                                                id="measurement_name_${index}" placeholder="Enter Measurement Name." />
                                        </div>

                                    </div>
                                    <div class="form-group col-md-8">
                                        <label>Measurement Column</label>
                                        <div class="form-group col-md-12">
                                            <input type="text" class="form-control w_90" name="measurement_column_${index}"
                                                id="measurement_column_${index}" placeholder="Enter Measurement Column." />
                                        </div>

                                    </div>
                                </div>
                                <button class="btn_round remove_node_btn_frm_field2" disabled>
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </div>
                `);
        }

        $(".form_field_outer2").find(".remove_node_btn_frm_field2:not(:first)").prop("disabled", false);
        $(".form_field_outer2").find(".remove_node_btn_frm_field2").first().prop("disabled", true);
    });
});
$(document).ready(function () {
    //===== delete the form fieed row
    $("body").on("click", ".remove_node_btn_frm_field2", function () {
        $(this).closest(".form_field_outer_row").remove();
        console.log("success");
    });
});


function changeMeasurement() {
    var e = document.getElementById("measurement_select");
    var index = e.selectedIndex;

    if (index == 1) {
        $(".form_field_outer2").children().remove();
        $(".form_field_outer2").append(`

    <div class="row form_field_outer_row">
        <div class="col-md-12 ">
            <div class="row ">
                <div class="col-md-4">
                    <label>Measurement Name</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_name_1"
                            id="measurement_name_1" placeholder="Enter Measurement Name." />
                    </div>

                </div>
                <div class="form-group col-md-8">
                    <label>Measurement Query</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_query_1"
                            id="measurement_query_1" placeholder="Enter Measurement Query." />
                    </div>

                </div>

            </div>
            <button class="btn_round remove_node_btn_frm_field2" disabled>
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    </div>
    `);
    }
    else if (index == 2) {
        $(".form_field_outer2").children().remove();
        $(".form_field_outer2").append(`

    <div class="row form_field_outer_row">
        <div class="col-md-12 ">
            <div class="row ">
                <div class="col-md-4">
                    <label>Measurement Name</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_name_1"
                            id="measurement_name_1" placeholder="Enter Measurement Name." />
                    </div>

                </div>
                <div class="form-group col-md-8">
                    <label>Measurement Query</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_query_1"
                            id="measurement_query_1" placeholder="Enter Measurement Query." />
                    </div>

                </div>

                <div class="col-md-4">
                    <label>Start Time</label>
                    <input type="text" class="form-control w_90" name="start_time_1"
                        id="start_time_1" placeholder="Start Time" />
                </div>
                <div class="col-md-4">
                    <label>End Time</label>
                    <input type="text" class="form-control w_90" name="end_time_1" id="end_time_1"
                        placeholder="End Time" />
                </div>
                <div class="col-md-4">
                    <label>Steps</label>
                    <input type="text" class="form-control w_90" name="steps_1" id="steps_1"
                        placeholder="Steps" />
                </div>

            </div>
            <button class="btn_round remove_node_btn_frm_field2" disabled>
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    </div>
    `);
    }
    else if (index == 3) {
        $(".form_field_outer2").children().remove();
        $(".form_field_outer2").append(`

    <div class="row form_field_outer_row">
        <div class="col-md-12 ">
            <div class="row ">
                <div class="col-md-4">
                    <label>Measurement Name</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_name_1"
                            id="measurement_name_1" placeholder="Enter Measurement Name." />
                    </div>

                </div>
                <div class="form-group col-md-8">
                    <label>Measurement Column</label>
                    <div class="form-group col-md-12">
                        <input type="text" class="form-control w_90" name="measurement_column_1"
                            id="measurement_column_1" placeholder="Enter Measurement Column." />
                    </div>

                </div>

            </div>
            <button class="btn_round remove_node_btn_frm_field2" disabled>
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    </div>
    `);
    }

}

function changePSP() {
    var e = document.getElementById("psp_select");
    var index = e.selectedIndex;
    if (index == 0) {
        document.getElementById("mtl_formula").value = ""

    }
    else if (index == 1) {
        document.getElementById("mtl_formula").value = "After {Q}, it is never the case that {P} [holds]."
    }
    else if (index == 2) {
        document.getElementById("mtl_formula").value = "After {Q}, it is never the case that {P} [holds] within X time units."
    }
    else if (index == 3) {
        document.getElementById("mtl_formula").value = "Before {R}, it is never the case that {P} [holds]."
    }
    else if (index == 4) {
        document.getElementById("mtl_formula").value = "Before  {R}, it is never the case that {P} [holds] within X time units."
    }
    else if (index == 5) {
        document.getElementById("mtl_formula").value = "Between {Q} and {R}, it is never the case that {P} [holds]."
    }
    else if (index == 6) {
        document.getElementById("mtl_formula").value = "Between {Q} and {R}, it is never the case that {P} [holds] between X and Y time units."
    }
    else if (index == 7) {
        document.getElementById("mtl_formula").value = "After {Q}, it is always the case that {P} [holds]."
    }
    else if (index == 8) {
        document.getElementById("mtl_formula").value = "After {Q}, it is always the case that {P} [holds] within X time units."
    }
    else if (index == 9) {
        document.getElementById("mtl_formula").value = "Before {R}, it is always the case that {P} [holds]."
    }
    else if (index == 10) {
        document.getElementById("mtl_formula").value = "Before {R}, it is always the case that {P} [holds] within X time units."
    }
    else if (index == 11) {
        document.getElementById("mtl_formula").value = "Between {Q} and {R}, it is always the case that {P} [holds] between X and Y time units."
    }
    else if (index == 12) {
        document.getElementById("mtl_formula").value = "Globally, {P} [holds] repeatedly every X time units."
    }
    else if (index == 13) {
        document.getElementById("mtl_formula").value = "Between {Q} and {R}, {P} [holds] repeatedly every X time units."
    }
    else if (index == 14) {
        document.getElementById("mtl_formula").value = "Globally, if {Q} [has occurred] then in response {P} [eventually holds] between X and Y time units."
    }
    else if (index == 15) {
        document.getElementById("mtl_formula").value = "Between {Q} and {R}, if {P} [has occurred] then in response {S} [eventually holds] between X and Y time units."
    }
}
