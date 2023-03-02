<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
if (empty($_POST['submit'])){
    echo <<<_END
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
      <head>
        <meta charset = "UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name = "description" content = "SpeakTheScript analyses input text and adds commas to improve its text to speech rendition. It also checks for heteronyms that may be mispronounced.">
        <meta name = "keywords" content = "text to speech, tts, commas, heteronyms, mispronounced words">
        <meta name = "author" content = "Louis-Philippe Bonhomme-Beaulieu">
        <link rel="stylesheet" href="speakthescript.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

        <title>Speak the Script</title>
    </head>
      <body>

      <nav class="navbar navbar-expand-lg navbar-dark" style="background-color:#6c757d;">
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarTogglerDemo03" aria-controls="navbarTogglerDemo03" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarTogglerDemo03">
          <ul class="navbar-nav mr-auto mt-2 mt-lg-0">
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com">Speak the Beats</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com/ReelTalk/">Reel Talk</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com/TouchdownTalk/">Touchdown Talk</a>
            </li>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com/All-TimeRhymes/">All-TimeRhymes<span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com/ConfidantQuotes/">Confidant Quotes</a>
            </li>
            <li class="nav-item active">
              <a class="nav-link" href="https://www.speakthebeats.com/SpeakTheScript/">Speak the Script<span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://www.speakthebeats.com/FixTheBeats/">Fix the Beats<span class="sr-only">(current)</span></a>
            </li>
          </ul>
        </div>
      </nav>

    <body style="background-color:#98d3e5;">
    <div>
        <div class="container-md">
        <div class="container px-4">
        <br><br><br>
        <h1><b>Welcome to Speak the Script!</b></h1>
        <img src="reading bird.jpg" width="500" height=auto alt="A bird punctuating the silence with song." class="img-fluid">
        <h2><b>SpeakTheScript helps you create more natural-sounding TTS!</b></h2>
        <p>Please enter some text and a revised script will be provided to you, allowing for improved text to speech (TTS) rendition. Some commas may be added where needed for more natural-sounding pauses, and the heteronyms will be changed to their corresponding Speech Synthesis Markup Language (SSML) "phoneme" tags
        and rendered according to their International Phonetic Alphabet (IPA) pronounciation.</p>


        <form method = 'POST'>
            <div class="form-floating">
                <textarea class="form-control" placeholder="Please paste your script here." name = "text" id="floatingTextarea2" style="height: 150px" maxlength="100000" required></textarea>
                <label for="floatingTextarea2">max 100,000 characters including line carriages and spaces</label>
        </form>
        <br><p>Select the desired English TTS accent:</p>
        <div class="btn-group btn-group-toggle" data-toggle="buttons">
        <label class="btn btn-secondary active">
          <input type="radio" name="English_Phonetics" id="option1" autocomplete="off" value = "American_English" checked> US English
        </label>
        <label class="btn btn-secondary">
          <input type="radio" name="English_Phonetics" id="option2" autocomplete="off" value = "British_English"> UK English
        </label>
        </div>

        <input name = "submit" type="submit" value="Speak the Script!" button type="button" class="btn btn-secondary btn float-right"></button>

        <br><br>
        <div class="alert alert-secondary alert-dismissible fade show" role="alert">
             <p>Be sure to also check out the interactive machine learning applications such as <i><b>Speak the Beats</i></b>, and related pages for movies (<i><b>Reel Talk</i></b>), Super Bowl commercials (<i><b>Touchdown Talk</i></b>), poems (<i><b>All-Time Rhymes</i></b>) and inspiring quotes (<b><i>Confidant Quotes</i></b>) as well as an automatic music arranger (<b><i>Fix the Beats</i></b>) in the navbar!</p>
             <button type="button" class="close" data-dismiss="alert" aria-label="Close">
             <span aria-hidden="true">&times;</span>
             </button>
             </div>
         </div>
        </div>
    _END;

}else{
    echo <<<_END
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset = "UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta name = "description" content = "SpeakTheScript analyses input text and adds commas to improve its text to speech rendition. It also checks for heteronyms that may be mispronounced.">
      <meta name = "keywords" content = "text to speech, tts, commas, heteronyms, mispronounced words">
      <meta name = "author" content = "Louis-Philippe Bonhomme-Beaulieu">
    <link rel="stylesheet" href="speakthescript.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    <script>
    function CopyToClipboard(id)
    {
    var r = document.createRange();
    r.selectNode(document.getElementById(id));
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(r);
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
    }
    </script>



    <title>Speak the Script</title>
    </head>
    <body>

    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color:#6c757d;">
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarTogglerDemo03" aria-controls="navbarTogglerDemo03" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarTogglerDemo03">
        <ul class="navbar-nav mr-auto mt-2 mt-lg-0">
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com">Speak the Beats</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com/ReelTalk/">Reel Talk</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com/TouchdownTalk/">Touchdown Talk</a>
          </li>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com/All-TimeRhymes/">All-TimeRhymes<span class="sr-only">(current)</span></a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com/ConfidantQuotes/">Confidant Quotes</a>
          </li>
          <li class="nav-item active">
            <a class="nav-link" href="https://www.speakthebeats.com/SpeakTheScript/">Speak the Script<span class="sr-only">(current)</span></a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.speakthebeats.com/FixTheBeats/">Fix the Beats<span class="sr-only">(current)</span></a>
          </li>
        </ul>
      </div>
    </nav>

    <body style="background-color:#98d3e5;">
    <div>
    <div class="container-md">
    <div class="container px-4">

    _END;

    #Here I am padding '\n' with a space on either side to prevent explode() splits from giving a word\n or \nword. This is important, as I am screening for heteronym matches and adding '**' on either side of the matches.
    $text = trim(preg_replace('/[\n]/', ' \n ', htmlspecialchars($_POST['text'])));
    #Pass in the "English_Phonetics" setting (British_English or American_English), if selected, in the query.
    #If the user forgot to select one, it will default to American_English in the Python code.
    if (isset($_POST['English_Phonetics'])){
      $English_Phonetics = $_POST['English_Phonetics'];
      $query = '"' . $text . '" ' . $English_Phonetics;
    }else{
        $query = '"' . $text . '"';
    }

    $command = escapeshellcmd("/home/ubuntu-server/anaconda3/bin/python3 /opt/lampp/htdocs/SpeakTheBeats/SpeakTheScript/speakthescript.py $query");
    $json = exec($command, $output, $return_var);
    if (!empty($json)) {
        $data = json_decode($json, true);
      #$associative_array_names is just for reference, it gives the sequence of names in $value. See python script 'speakthescript.py', where the following note is found: #All of the data will be outputed in a single dictionary (entireData_dictionaries), whose sole key is mapped to a value consisting of a list of
      #six dictionaries/lists/strings. The title of the individual dictionaries (sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas) give insight as to the structure of the dictionaries: KeyNames_ValueName1ValueName2ValueName3.
      $associative_array_names = array("sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas, number_of_heteronym_substitutions, whole_text");

    echo <<<_END
      <br>
      <br>
              <h1>Speak the Script - Here are the results: </h1>
    _END;

      #I need to 'unravel' the overarching dictionary $data to access $value, which is a list of dictionaries/lists/strings (see $associative_array_names for the sequence of dictionaries/lists/strings in the list)
      foreach ($data as $key => $value) {
        if (count(array_filter($value[0])) > 0){
           echo <<<_END
           <br>
           <div class="card" style="background-color:#faf0e5;">
               <div class="card-body">
                   <h2 class="card-title">-Sentences with Many Commas-</h2>
                   <hr>
                   <p class="card-text"><h3>List of sentences that may have too many commas:</h3></p>
               </div>
           </div>
           <br>
           _END;
      foreach ($data as $key => $value) {
          #$many_commas_sentence_count allows give a sentence number to every sentence in the dictionary $value[3], which is equivalent to the dictionary 'sentencesManyCommas_sentenceIndex' in the python script 'speakthescript.py'
          $many_commas_sentence_count = 1;
          foreach($value[0] as $key_sentencesManyCommas_sentenceIndex => $value_sentencesManyCommas_sentenceIndex) {
          #removing superfluous characters (left over after splitting dialogs at the period before the closing quotes) at start of sentence for clarity (the whole_text retains all information)
          $sentenceWords = explode(" ", $key_sentencesManyCommas_sentenceIndex);
          $sentenceWords[0] = str_replace(array('”', "’"), array("", ""), $sentenceWords[0]);
          for($t = 0; $t < count($sentenceWords); ++$t) {
          $sentenceWords[$t] = trim($sentenceWords[$t]);
          }
          $sentence = implode(" ", $sentenceWords);
          $key_sentencesManyCommas_sentenceIndex = trim(str_replace(array('\n'), array(" "), $sentence));
         echo <<<_END
         <div class="card" style="background-color:#faf0e5;">
         <div class="card-body">
         <h4 class="card-title">Sentence with many commas #$many_commas_sentence_count:</h4>
         <hr>
         <p class="card-text">$key_sentencesManyCommas_sentenceIndex</p>
         </div>
         </div>
         <br>
         _END;
         $many_commas_sentence_count += 1;
      }
      }
      }
      }



      foreach ($data as $key => $value) {
        if (count(array_filter($value[1])) > 0){
           echo <<<_END
           <br>
           <div class="card" style="background-color:#f5fae5;">
               <div class="card-body">
                   <h2 class="card-title">-Long Sentences-</h2>
                   <hr>
                   <p class="card-text"><h3>List of sentences that may require further commas, in addition to the commas added by Speak the Script:</h3></p>
               </div>
           </div>
           <br>
           _END;

      foreach ($data as $key => $value) {
          $long_sentence_count = 1;
          foreach($value[1] as $key_sentencesFewCommas_sentenceIndex => $value_sentencesFewCommas_sentenceIndex) {
            $sentenceWords = explode(" ", $key_sentencesFewCommas_sentenceIndex);
            $sentenceWords[0] = str_replace(array('”', "’"), array("", ""), $sentenceWords[0]);
            for($t = 0; $t < count($sentenceWords); ++$t) {
            $sentenceWords[$t] = trim($sentenceWords[$t]);
            }
            $sentence = implode(" ", $sentenceWords);
            $key_sentencesFewCommas_sentenceIndex = trim(str_replace(array('\n'), array(" "), $sentence));
               echo <<<_END
               <div class="card" style="background-color:#f5fae5;">
               <div class="card-body">
               <h4 class="card-title">Sentence with few commas #$long_sentence_count:</h4>
               <hr>
               <p class="card-text">$key_sentencesFewCommas_sentenceIndex</p>
               </div>
               </div>
               <br>
               _END;
            $long_sentence_count += 1;
      }
      }
      }
      }





      foreach ($data as $key => $value) {
        if (count(array_filter($value[2])) > 0){
                  echo <<<_END
                  <br>
                  <div class="card" style="background-color: #ddddee;">
                  <div class="card-body">
                  <h2 class="card-title">-Potentially Mispronounced Capitalized Words-</h2>
                  <hr>
                  <p class="card-text"><h3>List of capitalized words in the text that may be mispronounced:</h3></p>
                  _END;
                  foreach($value[2] as $key_potentiallyMispronouncedWords_wordCounts => $value_potentiallyMispronouncedWords_wordCounts) {
                    if (ctype_alpha($key_potentiallyMispronouncedWords_wordCounts)){
                  echo <<<_END
                  <p class="card-text">&#8226; $key_potentiallyMispronouncedWords_wordCounts : $value_potentiallyMispronouncedWords_wordCounts counts in whole text</p>
                  _END;
                  }
                  }
                  echo <<<_END
                  </div>
                  </div>
                  <br>
                  _END;


      }
      }


      foreach ($data as $key => $value) {
        if (count(array_filter($value[3])) > 0){
          foreach($value[3] as $key_percent_increase_in_commas => $value_percent_increase_in_commas) {

      }
      }
      }
      #The value of 'value_percent_increase_in_commas' outputed by the python script is either a percent value ('[\d]+%') or,
      #if there were no commas in the initial text : "There were no commas nor semicolons in the initial text and there are now n commas in the script after modifications."
      foreach ($data as $key => $value) {
        if (count(array_filter($value[3])) > 0){
          if (substr($value_percent_increase_in_commas, -1) === "%") {
           echo <<<_END
           <br>
           <div class="card">
               <div class="card-body">
                   <h2 class="card-title">-Modified Text-</h2>
                   <hr>
                   <p class="card-text"><h3>Here is the text with the heteronym substitutions to the International Phonetic Alphabet (IPA) fomat and/or added commas:</h3></p>
                   <p class="card-text">&#8226; $value_percent_increase_in_commas increase in commas throughout the text after modifications</p>
                   <p class="card-text">&#8226; $value[4] heteronym substitutions carried out throughout the text</p>
               </div>
           </div>
           <br>
           _END;

         }else{
           echo <<<_END
           <br>
           <div class="card">
               <div class="card-body">
                   <h2 class="card-title">-Modified Text-</h2>
                   <hr>
                   <p class="card-text"><h3>with the heteronym substitutions to the International Phonetic Alphabet (IPA) fomat and/or added commas:</h3></p>
                   <p class="card-text">&#8226; $value_percent_increase_in_commas</p>
                   <p class="card-text">&#8226; $value[4] heteronym substitutions carried out throughout the text</p>
               </div>
           </div>
           <br>
           _END;
         }


      foreach ($data as $key => $value) {
          $whole_text = str_replace(array('\n', "\?"), array("<br>", "?"), htmlentities($value[5]));
            #I found a useful javascript function 'function CopyToClipboard(id)' online to add a copy text button, which allows to copy to clipboard the text displayed on screen within the p class with id "wholetext".
            echo <<<_END
            <input name = "submit" type="submit" value="Copy Modified Text" button type="button" class="btn btn-secondary btn float-right" onclick="CopyToClipboard('wholeText');return false;"></button>
            <br><br>
            <div class="card">
            <div class="card-body">
            <p class="card-text" id = "wholeText">$whole_text</p>
            </div>
            </div>

            <br>
            _END;
      }
      }
      }


}else{
  echo <<<_END
  <br>
  <div class="card">
      <div class="card-body">
          <h1 class="card-title">Something Went Wrong...</h1>
          <hr>
          <p class="card-text"><h4>Please go back and enter at least two sentences.<br>
          <br>
      </div>
  </div>
  _END;
 }
 }

 ?>
