#pragma once

#include "../libafanasy/msgclasses/msgclassuserhost.h"

#include "../libafqt/qafclient.h"

#include "infoline.h"
#include "labelversion.h"
#include "watch.h"

#include <QtCore/QLinkedList>
#include <QtCore/QTimer>
#include <QBoxLayout>
#include <QLabel>
#include <QListWidget>
#include <QMainWindow>
#include <QWidget>

class ButtonOut;
class ButtonMonitor;
class ListItems;
class OfflineScreen;
class LabelVersion;

class QHBoxLayout;
class QVBoxLayout;
class QScrollArea;

class Dialog : public QMainWindow
{
    Q_OBJECT

public:
    Dialog();
    ~Dialog();

    inline bool isInitialized() const { return m_initialized; }
    inline bool isConnected()   const { return m_connected;   }

    void inline displayInfo(    const QString &message) { m_infoline->displayInfo(    message); }
    void inline displayWarning( const QString &message) { m_infoline->displayWarning( message); }
    void inline displayError(   const QString &message) { m_infoline->displayError(   message); }

	void inline announce( const std::string & i_str) { m_labelversion->showMessage( i_str);}

    void sendMsg( af::Msg * msg);

    bool openMonitor( int type, bool open);

    void repaintStart( int mseconds = 1000);
    void repaintFinish();

    void reloadImages();

    void keyPressEvent(    QKeyEvent         * event);

signals:
    void stop();

private slots:
	void showMenuLevel();
	void showMenuTheme();
	void showMenuPrefs();
	void showMenuHelp();

    void newMessage( af::Msg * msg);
    void connectionLost();
    void repaintWatch();

    void actColors();
    void actNotifications();
    void actSavePreferencesOnExit();
    void actSaveGUIOnExit();
	void actSaveHotkeysOnExit();
    void actSaveWndRectsOnExit();
    void actSavePreferences();
    void actShowOfflineNoise();
	void actGuiTheme( QString theme);
    void actGuiLevel( int i_level);
	void actShowDocs();
	void actShowForum();

protected:
    void contextMenuEvent( QContextMenuEvent * event);
    void closeEvent(       QCloseEvent       * event);
    void paintEvent ( QPaintEvent * event );

private:
	void createMenus();

    void sendRegister();
	void idReceived( int i_id, int i_uid = -1);
    void closeList();
    void connectionEstablished();
    void setDefaultWindowTitle();

private:
	QMenu * m_contextMenu;
	QMenu * m_levelMenu;
	QMenu * m_themeMenu;
	QMenu * m_prefsMenu;
	QMenu * m_helpMenu;

    bool m_initialized;
    bool m_connected;

    int m_monitorType;

	afqt::QAfClient m_qafclient;

    ListItems * m_listitems;
    OfflineScreen * m_offlinescreen;
    InfoLine * m_infoline;
    LabelVersion * m_labelversion;

    QHBoxLayout * m_hlayout_a;
    QVBoxLayout * m_vlayout_a;
    QHBoxLayout * m_hlayout_b;
    QVBoxLayout * m_vlayout_b;

    QTimer m_repaintTimer;

    ButtonMonitor * m_btnMonitor[Watch::WLAST];

    ButtonOut * m_btn_out_left;
    ButtonOut * m_btn_out_right;

    af::MsgClassUserHost m_mcuserhost;

    QPixmap m_img_top;
    QPixmap m_img_topleft;
    QPixmap m_img_topright;
    QPixmap m_img_bot;
    QPixmap m_img_botleft;
    QPixmap m_img_botright;

//	QWidget * m_topleft;
	QLabel * m_topleft;
    QWidget * m_topright;

    static int ms_size_border_top;
    static int ms_size_border_bot;
    static int ms_size_border_left;
    static int ms_size_border_right;
};
