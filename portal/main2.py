import BTSeeding

if __name__ == '__main__':
    username = "pyang.pepsico"
    password = "C0mpuw@r3"
    portal = BTSeeding.BTSeedingPortal(username, password)
    portal.login()
    portal.saveChartToScreenshot("Home page - Performance Map", cropChart=True)
    portal.close()
