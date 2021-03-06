import React from 'react';
import ciscoLive from '../Assets/clus-logo.png';
import allIn from '../Assets/all-in.png';
import devDash from '../Assets/DevDash2.png';
import { AppBar, Toolbar, Box, makeStyles } from '@material-ui/core';


const useStyles = makeStyles({
    logo: {
      width: 150,
      height: 40
    },
    dash: {
        width: 150,
        height: 35
    }
  });

const Header = () => {
    const classes = useStyles();

    return (
        <AppBar position="static" color="primary">
            <Toolbar display="flex" p={1}>
                <Box p={1} flexGrow={2} alignSelf="flex-start">
                    <img className={classes.logo} alt="CiscoLive" src={ciscoLive} />
                </Box>
                <Box p={1} flexGrow={2} alignSelf="center">
                    <img className={classes.dash} alt="DevDash" src={devDash}/>
                </Box>
                <Box p={1} flexGrow={0} alignSelf="flex-end">
                    <img className={classes.logo} alt="AllIn" src={allIn} />
                </Box>
            </Toolbar>
        </AppBar>
    )
}

export default Header