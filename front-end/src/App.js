import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {

  const [data, setData] = useState([{}]);

  useEffect(()=>{
    axios.get('http://localhost:5000/test').then(response => {
      console.log("SUCCESS", response)
      setData(response)
    }).catch(error => {
      console.log(error)
    })

  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <p>React + Flask Tutorial</p>
        <div>{data.status === 200 ? 
          <h3>{data.data.message}</h3>
          :
          <h3>LOADING</h3>}</div>
      </header>
    </div>
  );
}

export default App;