$(document).ready(function(){
	var all_quarters_data;
	var current_quarter;
	var current_play_index = 0;
	var play_timeout = 100;

	function set_game_state_for_play(play_data) {
		$("#play_description").html(play_data.desc);
		$("#football_pos").css({left: posteam_yrds(play_data.awayteam, play_data.posteam, play_data.yrdln, play_data.yards_gained, play_data.yrdline100)});
		var calc_left =  firstdown_line(play_data.awayteam,play_data.posteam, play_data.yrdline100, play_data.ydstogo);
		$("#first_down_line").css({left: calc_left});
		
		$(".quarter_number").html(play_data.qtr);
		$(".time_left").html(play_data.game_time);
		$(".current_down").html(play_data.down);
		$(".yards_to_go").html(play_data.ydstogo);
		$(".team1").html(play_data.hometeam);
		if (play_data.posteam == play_data.hometeam) {
			$(".team1_score").html(play_data.posteamscore);
			$(".team2_score").html(play_data.defteamscore);
		}
		else if (play_data.defensiveteam == play_data.hometeam) {
			$(".team1_score").html(play_data.defteamscore);
			$(".team2_score").html(play_data.posteamscore);
		}
		
		$(".team2").html(play_data.awayteam);
		
		$(".side_of_field").html(play_data.sideoffield);
		$(".yard_line").html(play_data.yrdln);

	}

	function yrds_to_pxl(in_yards){
		return in_yards*9.75;
	}

	function posteam_yrds(awayteam, posteam, yrdln, yrds_gained, yrdline100){
		if (posteam == awayteam) {
			return ((yrds_to_pxl(yrdline100-yrds_gained) + 95) + "px");
		}
		else if (posteam !== awayteam){
			return ((1073 - yrds_to_pxl(yrdline100-yrds_gained)) + "px");
		}
	}

	function firstdown_line(awayteam, posteam, yrdline100, yrds_to_go){
		if (posteam == awayteam) {
			return ((yrds_to_pxl(yrdline100-yrds_to_go) + 95) + "px");
		}
		else if (posteam !== awayteam){
			return ((1073 - yrds_to_pxl(yrdline100-yrds_to_go)) + "px");
		}	 
	}

	function perform_next_play() {
		var quarter_data = all_quarters_data[current_quarter];
		current_play = quarter_data[current_play_index];
		if (current_play.playtype == 'Kickoff' || current_play.playtype == 'Punt' || current_play.playtype == 'Field Goal' || current_play.playtype == 'Timeout'){

		}
		else{
			set_game_state_for_play(current_play);
		}
    	if (quarter_data.length == current_play_index + 1) {
    		if (current_quarter < 4) {
    			current_quarter += 1;
    			current_play_index = 0;
    			setTimeout(perform_next_play, play_timeout);
    		} else {
    			// GAME OVER
    			// console.log(quarter_data[quarter_data.length-2])
    			last_play_data = quarter_data[quarter_data.length-2]
    			$(".team1_score").html(last_play_data.posteamscore);
				$(".team2_score").html(last_play_data.defteamscore);
    			$("#gameover").show();
    		}
    	} 
    	else {
    		current_play_index += 1;
    		setTimeout(perform_next_play, play_timeout);
    	}
	}
	$("#gameover").hide();
	var url = $("#game_data_url").val();
	$.get(url, function(data){
	  $("#loading").hide();
	  /*
	  	$.each(data, function(index,val){
	  	console.log(index, data[index]);
	  	quarter_data = data[index];
	  	current_play_index = 0;
	  	console.log(index,current_play_index);
	  })
	  */
	  	all_quarters_data = data;
	  	current_quarter = 1;
	  	perform_next_play();

	});
});