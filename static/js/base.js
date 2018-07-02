$(document).ready(function(){
	var first_quarter_data;
	var current_play_index = 0;
	var play_timeout = 3000;

	function set_game_state_for_play(play_data) {
		$("#play_description").html(play_data.desc);
		$("#football_pos").css({left: posteam_yrds(play_data.posteam, play_data.yrdln, play_data.yards_gained, play_data.sideoffield)});
		console.log(play_data.yrdln, play_data.yards_gained)
		var calc_left =  firstdown_line(play_data.posteam, play_data.yrdln, play_data.ydstogo);
		$("#first_down_line").css({left: calc_left});

	}

	function yrds_to_pxl(in_yards){
		return in_yards*11.3;
	}

	function posteam_yrds(posteam, yrdln, yrds_gained, sideoffield){
		if (posteam == "NE" && (yrdln+yrds_gained)<50) {
			return ((yrds_to_pxl(yrdln+yrds_gained) + 95) + "px");
		}
		else if (posteam == "NE" && (yrdln+yrds_gained)>50 && posteam !== sideoffield){
			return ((yrds_to_pxl(100-(yrdln+yrds_gained))) + 95 + "px")
		}
		else if (posteam == "PIT" && (yrdln+yrds_gained)<50){
			return ((1073 - yrds_to_pxl(yrdln+yrds_gained)) + "px");
		}
		else if (posteam == "PIT" && (yrdln+yrds_gained)>50 && posteam == sideoffield){
			return ((1073 - yrds_to_pxl(100-(yrdln+yrds_gained))) + "px");
		}
	}

	function firstdown_line(posteam, yrdln, yrds_to_go){
		if (posteam == "PIT") {
			return ((yrds_to_pxl(yrdln+yrds_to_go) + 95) + "px");
		}
		else if (posteam == "NE"){
			return ((1073 - yrds_to_pxl(yrdln+yrds_to_go)) + "px");
		}	 
	}

	function perform_next_play() {
		current_play = first_quarter_data[current_play_index];
		if (current_play.playtype !== 'Kickoff' || current_play.playtype !== 'Punt' || current_play.playtype !== 'Field Goal'){
			set_game_state_for_play(current_play);
    	if (first_quarter_data.length == current_play_index + 1) {

    	} else {
    		current_play_index += 1;
    		setTimeout(perform_next_play, play_timeout);
    	}
		}
	}

	$.get("/2013110309", function(data){
	  first_quarter_data = data[1];
	  setTimeout(perform_next_play, play_timeout);
	});
});