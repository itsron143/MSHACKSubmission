class Awesome extends React.Component {
  render() {
    return (
      <div>
        <h1>Hello, World!</h1>
        <h4>Skeleton - A dead simple, responsive boilerplate.</h4>
        <a className="button button-primary u-pull-left" href="https://codepen.io/pen?template=xObVBe" target="_blank">Use this template!</a><a className="button button-primary u-pull-right" href="http://getskeleton.com" target="_blank">getskeleton.com</a>
      </div>
    )
  }
}

ReactDOM.render(
  <Awesome />,
  document.getElementById('yes')
);
