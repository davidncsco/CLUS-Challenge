import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';
import AnimatedChoiceButtons from '../components/styles/Button.styled'
import StopWatch from '../components/StopWatch'

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
    width: 960px;
    height: 540px;
    object-fit: full-width;
`;


const Challenge = () => {
    const classes = useStyles();
    const navigate = useNavigate();
    const [answer,setYourAnswer] = useState();
    const [dialogTitle,setDialogTitle] = useState('')
    const [qindex,setQIndex] = useState(1)
    const [openDialog,setOpenDialog] = useState(false)
    const [endofChallenge,setEndOfChallenge] = useState(false)
    const [wrongs, setWrongs] = useState(0)

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
      let car_position = {"number": car.number, "position": car.position}
      console.log('new car position=',car_position)
      localStorage.setItem("car",JSON.stringify(car_position))
    }

    function sendCommandToCar(car,distance) {
      console.log('Send AXIOS command to car for user',userid,'with distance',distance)
      const url = `${process.env.REACT_APP_API_URL}/score?user_id=${userid}&weight=${distance}`
      console.log(url)
      axios.put(url)
      .then(response => {
          console.log(response.data)
          saveCarPositionInLocalStorage(distance)
      })
      .catch( error => {
          console.log(error.response)
          alert('Cannot send axios command to car for user:',car.userid)
      })
    }

    function recordUserTime() {
      console.log('Send AXIOS command to record user time')
      // End of challenge - Record user time in DB for leader board display
      let url = `${process.env.REACT_APP_API_URL}/end?userid=${userid}`
      console.log(url)
      axios.put(url)
      .then(response => {
          saveCarPositionInLocalStorage(-1 * car.position)
      })
      .catch( error => {
          console.log(error.response)
          alert('Cannot record time of challenge completion for user with id=',userid)
      })
    }

    useEffect( () => {
      console.log('Enter userEffect...qindex=',qindex,'answer=',answer)
      if( answer !== undefined ) {    // answer is right or wrong
        if(qindex <= questions.length) {
            // Compute distance to go back/forth for the car
            let weight = ( questions[qindex-1].weight === null ) ? 1 : questions[qindex-1].weight
            let distance = (answer ? 1: -1) * weight
            sendCommandToCar(car,distance)
        }
        setOpenDialog(true)
        if( answer && qindex === questions.length) {
            setEndOfChallenge(true)
            recordUserTime()
        }
      }
    }, [answer,qindex]);

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
      if( answer && qindex < questions.length ) {
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
                <Typography color="textSecondary" variant="h6">
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
                    <DialogTitle>Congratulations</DialogTitle>
                    <DialogContent>
                      <DialogContentText>
                        You have completed the DevRel500 challenge with {questions.length} questions and
                        you answered {wrongs} time(s) incorrectly. Please check the leader board for your standing.
                      </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                      <Button onClick={handleOnEndOfGame} color="primary" autoFocus>
                        Close
                      </Button>
                    </DialogActions>
                  </Dialog>
                )}
            </Container>
        </Container>
    );
}

export default Challenge;