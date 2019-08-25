#!/usr/bin/perl
#
# IRC Bot for Hermod Telegram Gateway. Works with telegramhook for receiving
# messages from a telegram group.
#
# 2019-08-17, Ruben de Groot
#
# Abandoned because of SSL problems. Use the python version instead

use strict;
use warnings;
use POE qw(Component::IRC Component::IRC::Plugin::FollowTail Component::SSLify);
use HTTP::Tiny;
use URI::Escape;
use JSON qw( decode_json );

my $cfg = "/etc/hermod.json";
open my $fh, '<', $cfg or die "error opening $cfg $!";
my $config = decode_json do { local $/; <$fh> };

my $ircname  = 'Hermod gateway from irc to telegram';
my $URL = "https://api.telegram.org/bot$config->{token}/sendMessage";

# We create a new PoCo-IRC object
my $irc = POE::Component::IRC->spawn(
   nick    => $config->{nick},
   ircname => $ircname,
   server  => $config->{ircnode},
   Port    => $config->{port},
   UseSSL  => $config->{usessl},
) or die "Oh noooo! $!";

POE::Session->create(
    package_states => [
        main => [ qw(_default _start irc_001 irc_public irc_tail_input ) ],
    ],
    heap => { irc => $irc },
);

$poe_kernel->run();

sub _start {
    my $heap = $_[HEAP];

    # retrieve our component's object from the heap where we stashed it
    my $irc = $heap->{irc};
    $irc->plugin_add( 'FollowTail' => POE::Component::IRC::Plugin::FollowTail->new(
        filename => $config->{telfile},
    ));
    $irc->yield( register => 'all' );
    $irc->yield( connect => { } );
    return;
}

sub irc_001 {
    my $sender = $_[SENDER];

    # Since this is an irc_* event, we can get the component's object by
    # accessing the heap of the sender. Then we register and connect to the
    # specified server.
    my $irc = $sender->get_heap();

    print "Connected to ", $irc->server_name(), "\n";

    # we join our channel
    $irc->yield( join => $config->{channel} );
    return;
}

sub irc_public {
  my ($sender, $who, $where, $what) = @_[SENDER, ARG0 .. ARG2];
  my $nick = ( split /!/, $who )[0];
  my @data;
  my $coin = '';
  return if ( $what =~ /forbidden words/ );
  # we relay all messages straight to telegram
  my $text = uri_escape("Msg in IRC $config->{channel} by $nick: $what");
  my $data = "chat_id=$config{chat_id}&text=$text";
  HTTP::Tiny->new->get( "$URL?$data" );
  return;
}

sub irc_tail_input {
    my ($kernel, $sender, $config->{telfile}, $input) = @_[KERNEL, SENDER, ARG0, ARG1];
    $irc->yield( privmsg => $config->{channel} => $input );
    return;
}

# We registered for all events, this will produce some debug info.
sub _default {
    my ($event, $args) = @_[ARG0 .. $#_];
    my @output = ( "$event: " );

    for my $arg (@$args) {
        if ( ref $arg eq 'ARRAY' ) {
            push( @output, '[' . join(', ', @$arg ) . ']' );
        }
        else {
            push ( @output, "'$arg'" );
        }
    }
    print join ' ', @output, "\n";
    die "I got disconnected :( :(\nKilling myself..\n" if grep(/irc_disconnect/,@output);
    return;
}

sub telepoller {
    my $reply = "Polling telegram\n";
    $irc->yield( privmsg => $config->{channel} => $reply );
    sleep 10;
}

