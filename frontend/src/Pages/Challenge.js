import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import ky from 'ky';
import AnimatedChoiceButtons from '../components/styles/Button.styled'
import StopWatch from '../components/StopWatch'
import useSound from 'use-sound'
import fanFare from '../Assets/fanfare.mp3'

// More Material UI examples
// https://react.school/material-ui/templates
import {
  makeStyles,
} from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Container from "@material-ui/core/Container";
import Dialog from "@material-ui/core/Dialog";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";

const useStyles = makeStyles((theme) => ({
  margin: {
    "& > *": {
      margin: theme.spacing(1)
    }
  },
  spacer: {
    marginBottom: theme.spacing(10)
  }
}));

const StyledImage = styled.img`
    width: 1200px;
    height: 650px;
    object-fit: full-width;
`;

const FINISH_LINE = 5

const Challenge = () => {
    const classes = useStyles();
    const navigate = useNavigate();
    const [answer,setYourAnswer] = useState();
    const [dialogTitle,setDialogTitle] = useState('')
    const [qindex,setQIndex] = useState(1)
    const [openDialog,setOpenDialog] = useState(false)
    const [endofChallenge,setEndOfChallenge] = useState(false)
    const [wrongs, setWrongs] = useState(0)
    const [play] = useSound(fanFare);
    const [carPosition,setCarPosition] = useState(0)

    // Information passing from registration page
    let location = useLocation()
    const firstname = location.state.first
    const userid    = location.state.userid
    const car       = location.state.car
    const questions = location.state.questions

    const [question,setNextQuestion] = useState(questions[qindex-1]);

    function saveCarPositionInLocalStorage(distance) {
      console.log('Save car positon to localStorage, distance=',distance)
      // If new position negative then reset it to 0
      car.position = ((car.position+distance) >= 0)? car.position+distance : 0
      console.log('Current car position',car.position)
      //let car_position = {"number": car.number, "position": car.position}
      //localStorage.setItem("car",JSON.stringify(car_position))
    }

    async function sendCommandToCar(car,distance) {
      console.log('Send KY command to car for user',car.number,'with distance',distance)
      const url = `${process.env.REACT_APP_API_URL}/score?carid=${car.number}&weight=${distance}`
      console.log(url)
      try {
        const json = await ky.put(url)
        console.log( json )
      } catch(error) {
        alert(`Can't send command to car ${car.number} error=${error}, please notify admin`)
      }
      saveCarPositionInLocalStorage(distance)
    }

    async function recordUserTime() {
      console.log('Send KY command to record user time')
      const url = `${process.env.REACT_APP_API_URL}/end?userid=${userid}&carid=${car.number}`
      console.log(url)
      try {
        const json = await ky.put(url)
        console.log( json )
      } catch(error) {
        alert(`Can't record user time in database ${error}, please notify admin`)
      }
    }

    useEffect( () => {
      console.log('Enter userEffect...qindex=',qindex,'answer=',answer)
      if( answer !== undefined ) {    // answer is right or wrong
        setOpenDialog(true)
        console.log('Current car position',car.position)
        if( answer && qindex === questions.length ){
          stopTheChallenge()
        }
      }
    }, [answer,qindex]);

    useEffect( () => {
      console.log('Enter useEffect for openDialog',openDialog,answer)
      if( (answer !== undefined) && (qindex < questions.length) ) {
          // Compute distance to go back/forth for the car
          let weight = ( questions[qindex-1].weight === null ) ? 1 : questions[qindex-1].weight
          let distance = (answer ? 1: -1) * weight
          sendCommandToCar(car,distance)
      }
    }, [openDialog])

    function stopTheChallenge() {
      console.log('!!! End of Challenge')
      setEndOfChallenge(true)
      recordUserTime()
      play()
    }

    function handleOnEndOfGame() {
      navigate("/",{state:{}})
    }

    function handleOnclick(choice) {    
        console.log('Enter handleOnClick...qindex:',qindex,'answer',answer)
        let result = question.answer.includes(choice)
        setDialogTitle(result ? 'That is correct!' : 'Incorrect!!!')
        setWrongs(result ? wrongs : wrongs+1 )
        setOpenDialog(true)
        setYourAnswer(result)
    }

    function handleNextQuestion() {
      console.log('Enter handleNextQuestion...qindex:',qindex,'answer',answer)
      setOpenDialog(false)
      if( car.position === FINISH_LINE ) {
          setOpenDialog(true)
          stopTheChallenge()
      } else if ( answer && qindex < questions.length ) {
          console.log('Index increment, set next question...')
          setNextQuestion(questions[qindex])
          setQIndex(qindex+1)
      }
      setYourAnswer(undefined)
    }

    return (
        <Container>
            <Typography color="textSecondary" variant="h6">
              Welcome {firstname} to DevRel500 challenge - You've been assigned to "{car.color}"" car
            </Typography>
            <Container >
                <StyledImage src={`${process.env.REACT_APP_API_URL}/static/${question.filename}`} alt="" id="img" className="img" />
            </Container>
            <Container className={classes.margin}>
                <Typography variant="h6">
                    Please select your answer
                </Typography>
                {question.choices.map((choice) => (
                    <AnimatedChoiceButtons id={choice} variant="contained" key={choice} onClick={() => handleOnclick(choice)}>
                    {choice}
                    </AnimatedChoiceButtons>
                ))}
                <StopWatch />
                {(openDialog) && (qindex <= questions.length) && (
                    <Dialog open={openDialog}>
                      <DialogTitle>{dialogTitle}</DialogTitle>
                      <DialogContent>
                        <DialogContentText>
                          Click next to continue
                        </DialogContentText>
                      </DialogContent>
                      <DialogActions>
                        <Button onClick={handleNextQuestion} color="secondary" autoFocus>
                          Next
                        </Button>
                      </DialogActions>
                    </Dialog>
                )}
                {openDialog && endofChallenge && (
                  <Dialog open={openDialog}>
                    <DialogTitle><span style={{color: 'red'}}>!!! CONGRATULATIONS !!!</span></DialogTitle>
                    <DialogContent>
                      <DialogContentText>
                        You have crossed the finish line. Among {qindex} questions, you answered {wrongs} time(s) incorrectly. Check the leaderboard for your standing.
                        Please click on the trumpet to end the game!
                      </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                      <button onClick={handleOnEndOfGame} color="lightblue" autoFocus>
                        <span role="img" aria-label="trumpet">
                          🎺
                        </span>                                                  
                      </button>
                    </DialogActions>
                  </Dialog>
                )}
            </Container>
        </Container>
    );
}

export default Challenge;