const Footer = () => {
  return (
    <footer style={{ backgroundColor: 'green', color: 'white', padding: '20px', textAlign: 'center' }}>
        &copy; {new Date().getFullYear()} Flare. All rights reserved.
      </footer>
  )
}

export default Footer